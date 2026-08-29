""" HTTP layer of the dependency downloader: cached fetches and failure diagnosis.

A download can fail because the machine is offline, because a firewall/antivirus filters HTTPS, or because
the API itself is down or blocking us.  These look identical from a single exception, so every failure is
translated into a sentence naming the likely culprit, backed by one probe of neutral hosts.

Two of those failures clear on their own: a throttled API, and a cache file still held by another process.
Both are retried with a growing delay before the build is told anything went wrong.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
import socket
import ssl
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import stouputils as stp
from beet import Cache, Context

# Constants
HEADERS: dict[str, str] = {"User-Agent": "StewBeet"}
""" Headers sent with every request, some APIs reject the default urllib user-agent. """

DOWNLOAD_ATTEMPTS: int = 4
""" Attempts allowed per download before the failure is reported. """

DOWNLOAD_DELAY: float = 2.0
""" Seconds before the second attempt, doubling from there, so a throttled API gets 2s, 4s and 8s to calm down. """

TRANSIENT_STATUS: frozenset[int] = frozenset({408, 425, 429, 500, 502, 503, 504})
""" HTTP statuses worth another attempt: throttling, and the server side failures that clear on their own. """

PROBE_URLS: tuple[str, ...] = ("https://one.one.one.one", "https://api.github.com")
""" Neutral hosts probed once when a download fails, to tell a local block apart from a failing service. """

PROBE_TIMEOUT: float = 5.0
""" Seconds allowed to each connectivity probe before considering the host unreachable. """

CONNECTIVITY: dict[str, bool] = {}
""" Cached probe result under the "reachable" key, filled the first time a download fails. """

CONNECTIVITY_LOCK: Lock = Lock()
""" Guards CONNECTIVITY since libraries are resolved from several threads. """

DOWNLOAD_LOCKS: dict[Path, Lock] = {}
""" One lock per cache file. Libraries are resolved in parallel and two of them can share a download URL,
which on Windows means one thread deleting or writing the file another still holds open.
"""

DOWNLOAD_LOCKS_GUARD: Lock = Lock()
""" Guards DOWNLOAD_LOCKS itself, filled from the resolver threads. """

HTTP_HINTS: dict[int, str] = {
	400: "malformed request",
	401: "authentication required",
	403: "access denied, the API or a firewall/CDN in between is blocking this client",
	404: "not found, the pack id or slug is probably wrong",
	429: "rate limited, too many requests were sent to this API",
	451: "blocked for legal reasons",
	500: "internal server error",
	502: "bad gateway, the API is down or restarting",
	503: "service unavailable, the API is down or overloaded",
	504: "gateway timeout, the API is too slow to answer",
}
""" Human explanation for the HTTP status codes these APIs realistically return. """

SOCKET_HINTS: dict[int, str] = {
	13: "socket access forbidden (EACCES), a local security policy is blocking the connection",
	101: "network unreachable (ENETUNREACH), no route to the internet",
	104: "connection reset by peer (ECONNRESET), something cut the connection mid-way",
	110: "connection timed out (ETIMEDOUT), packets are being dropped, typically by a firewall",
	111: "connection refused (ECONNREFUSED), nothing is listening on the other side",
	113: "host unreachable (EHOSTUNREACH), no route to that host",
	10013: "socket access forbidden (WinError 10013), a firewall or antivirus is blocking the connection",
	10054: "connection reset by peer (WinError 10054), something cut the connection mid-way",
	10060: "connection timed out (WinError 10060), packets are being dropped, typically by a firewall",
	10061: "connection refused (WinError 10061), nothing is listening on the other side",
	10065: "host unreachable (WinError 10065), no route to that host",
	11001: "host not found (WinError 11001), DNS could not resolve the name",
}
""" Human explanation per socket error, keyed by Windows error code when available, else by errno. """


# Classes
class TransientDownloadError(Exception):
	""" A failure worth another attempt, wrapping the real one as its cause.

	The retry decorator selects on the exception type, while the diagnosis needs the original exception to
	name the culprit, so the two are kept apart rather than reported as one another.
	"""


# Functions
def is_transient(exc: BaseException) -> bool:
	""" Whether *exc* is worth another attempt: a throttled API, a cut connection, or a locked cache file.

	Args:
		exc (BaseException): The exception raised while downloading.
	Returns:
		bool: True when waiting and trying again can plausibly succeed.

	Examples:
		>>> is_transient(HTTPError("", 429, "Too Many Requests", {}, None))
		True
		>>> is_transient(HTTPError("", 404, "Not Found", {}, None))
		False
		>>> is_transient(PermissionError(13, "being used by another process"))
		True
		>>> is_transient(URLError(ConnectionResetError()))
		True
	"""
	if isinstance(exc, HTTPError):
		return exc.code in TRANSIENT_STATUS
	if isinstance(exc, URLError):
		return isinstance(exc.reason, BaseException) and is_transient(exc.reason)
	return isinstance(exc, PermissionError | ConnectionError | TimeoutError)


def download_lock(target: Path) -> Lock:
	""" The lock owning *target*, created on first use. """
	with DOWNLOAD_LOCKS_GUARD:
		return DOWNLOAD_LOCKS.setdefault(target, Lock())


def internet_reachable() -> bool:
	""" Return whether any neutral host answers, probing at most once per build. """
	with CONNECTIVITY_LOCK:
		if "reachable" not in CONNECTIVITY:
			CONNECTIVITY["reachable"] = any(host_answers(url) for url in PROBE_URLS)
		return CONNECTIVITY["reachable"]


def host_answers(url: str) -> bool:
	""" Return whether *url* answered anything at all, an HTTP error still counting as an answer. """
	try:
		with urlopen(Request(url, headers=HEADERS), timeout=PROBE_TIMEOUT):
			return True
	except HTTPError:
		return True
	except Exception:
		return False


def connectivity_verdict() -> str:
	""" Suffix naming the culprit, since a dead service and a blocked machine look identical from one failure. """
	if internet_reachable():
		return " | other websites answer fine, so this host is down or blocking you"
	return " | no website answers at all, so this machine is offline or a firewall/proxy blocks outgoing HTTPS"


def socket_hint(exc: OSError) -> str:
	""" Explain a socket-level failure, keyed by Windows error code when there is one, else by errno. """
	code: int | None = getattr(exc, "winerror", None) or exc.errno
	return SOCKET_HINTS.get(code, str(exc)) if code else (str(exc) or type(exc).__name__)


def describe_network_error(url: str, exc: BaseException) -> str:
	""" Turn a raw download exception into a one-line diagnosis naming the likely culprit.

	Args:
		url  (str):           The URL that failed, used to report the host name.
		exc  (BaseException): The exception raised while downloading.
	Returns:
		str: The diagnosis, ex: "HTTP 503 Service Unavailable from api.smithed.dev: the API is down or overloaded"

	Examples:
		>>> describe_network_error("https://api.smithed.dev/v2/packs/x", HTTPError("", 404, "Not Found", {}, None))  # doctest: +ELLIPSIS
		'HTTP 404 Not Found from api.smithed.dev: not found, ...'
	"""
	host: str = urlsplit(url).hostname or url
	if isinstance(exc, TransientDownloadError) and exc.__cause__ is not None:
		return f"still failing after {DOWNLOAD_ATTEMPTS} attempts, {describe_network_error(url, exc.__cause__)}"
	if isinstance(exc, HTTPError):
		fallback: str = "the server refused the request" if exc.code < 500 else "the server failed to answer"
		return f"HTTP {exc.code} {exc.reason} from {host}: {HTTP_HINTS.get(exc.code, fallback)}"

	reason: object = exc.reason if isinstance(exc, URLError) else exc
	if isinstance(reason, ssl.SSLCertVerificationError):
		return f"TLS certificate of '{host}' rejected ({reason}): HTTPS is being intercepted by an antivirus/proxy, or the CA bundle is outdated"
	if isinstance(reason, ssl.SSLError):
		return f"TLS handshake with '{host}' failed ({reason}): traffic is being filtered by a firewall or a proxy{connectivity_verdict()}"
	if isinstance(reason, socket.gaierror):
		return f"DNS lookup failed for '{host}' ({reason.strerror}): no internet connection, or DNS is blocked locally{connectivity_verdict()}"

	# A filesystem error names the file it failed on, a socket one does not, which is what tells them apart.
	# Probing the network for a locked cache file would blame the host for something local.
	if isinstance(reason, OSError) and reason.filename is not None:
		return f"{reason.strerror} on '{reason.filename}': the cache file is held by another process, typically an antivirus or a parallel build"
	if isinstance(reason, OSError):
		return f"{socket_hint(reason)} while contacting '{host}'{connectivity_verdict()}"
	return f"{type(exc).__name__} while contacting '{host}': {exc}"


def describe_body(text: str) -> str:
	""" Describe a response that is not the expected JSON, so a proxy or captive-portal page is obvious.

	Examples:
		>>> describe_body("<html>Blocked</html>")
		'HTML received instead of JSON (proxy, captive portal or error page): <html>Blocked</html>'
	"""
	snippet: str = " ".join(text.split())[:200]
	if not snippet:
		return "empty response, the connection was cut before any data arrived"
	if snippet.startswith(("<", "﻿<")):
		return f"HTML received instead of JSON (proxy, captive portal or error page): {snippet}"
	return snippet


@stp.retry(exceptions=TransientDownloadError, max_attempts=DOWNLOAD_ATTEMPTS, delay=DOWNLOAD_DELAY, backoff=2.0, message="Download failed")
def attempt_download(cache: Cache, url: str, target: Path) -> Path:
	""" One download attempt, never letting a previously failed one masquerade as a hit.

	beet creates the destination file before fetching, so a failed download leaves a 0-byte file that every
	later build happily reuses, hiding the real error behind a bogus parsing failure.
	"""
	try:
		if target.is_file() and target.stat().st_size == 0:
			target.unlink()
			stp.debug(f"Discarded the empty cache entry left by a previous failed download of '{url}'.")

		result: Path = cache.download(url, target, headers=HEADERS)
		if result.stat().st_size == 0:
			result.unlink(missing_ok=True)
			raise ConnectionError("the server accepted the request but sent an empty body")
		return result
	except Exception as exc:
		if is_transient(exc):
			raise TransientDownloadError(f"'{url}': {exc}") from exc
		raise


def download_to_cache(ctx: Context, url: str, path: Path | None = None) -> Path:
	""" Download *url* through beet's cache, one thread at a time per file, retrying what can still succeed. """
	cache: Cache = ctx.cache["stewbeet"]
	target: Path = path if path is not None else cache.get_path(url)
	with download_lock(target):
		return attempt_download(cache, url, target)


def cached_json(ctx: Context, url: str) -> Any | None:
	""" Download and parse a JSON document, reporting why it failed instead of a bare parsing error. """
	try:
		path: Path = download_to_cache(ctx, url)
	except Exception as exc:
		stp.warning(f"Failed to fetch '{url}': {describe_network_error(url, exc)}")
		return None

	text: str = path.read_text(encoding="utf-8", errors="replace")
	try:
		return json.loads(text)
	except json.JSONDecodeError as exc:
		path.unlink(missing_ok=True)
		stp.warning(f"Invalid JSON from '{url}' ({exc.msg}): {describe_body(text)}")
		return None


def cached_zip(ctx: Context, url: str) -> Path | None:
	""" Download *url* via beet cache, ensuring the file has a ``.zip`` suffix. """
	if not url or url == "can't find":
		return None
	try:
		path: Path = ctx.cache["stewbeet"].get_path(url)
		return download_to_cache(ctx, url, path if path.suffix else path.with_suffix(".zip"))
	except Exception as exc:
		stp.warning(f"Failed to download '{url}': {describe_network_error(url, exc)}")
		return None

