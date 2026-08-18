""" HTTP front of the sandbox: one job at a time, each in a throwaway process.

Deliberately stdlib only, and it never imports stewbeet. The worker has to outlive every way a job
can die, so it stays a few megabytes of interpreter that cannot be broken by anything a build does to
its own address space. jobs.py holds the ceilings and the kill path, builds.py the two jobs
themselves; what is here is only the protocol.

The container is the security boundary, not this file: `internal: true` networking, `read_only`
rootfs, `cap_drop: ALL` and the memory cgroup are what make running submitted Python acceptable.
"""
# Imports
import base64
import json
import shutil
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from builds import Build, Headers
from jobs import SRV, Job
from selftest import selftest

# Constants
PORT: int = 8000
""" Only ever reached over the internal compose network, never published to the host. """

MAX_CODE_BYTES: int = 16 * 1024
""" Also enforced on the web side. Repeated here because the worker cannot assume its caller. """

MAX_PACK_BYTES: int = 25 * 1024 * 1024
""" Largest upload /headers accepts, matching MAX_PACK_BYTES in src/api/sandboxLimits.ts. """

QUEUE_TIMEOUT: float = 2.0
""" How long a request waits for the single job slot before being told to come back. """

MIN_FREE_BYTES: int = 32 * 1024 * 1024
""" Refuse to start a build when /tmp has less room than this, rather than failing halfway. """

MIN_HEADERS_FREE_BYTES: int = 256 * 1024 * 1024
""" The same for /headers, sized for the upload, its extracted form and the archive written back. """

MAX_META_CHARS: int = 4 * 1024
""" Ceiling on the metadata header, so a talkative job cannot produce a response nothing parses. """

MAX_WARNINGS: int = 40
""" First cut at the warning list, before the header ceiling trims whatever still does not fit. """

META_HEADER: str = "X-Sandbox-Meta"
""" Where a zip response carries what its body has no room for. Read by src/api/headers.ts. """

HEADERS_STATUS: dict[str, int] = {
	"invalid_archive": 400,
	"no_pack_mcmeta": 400,
	"too_many_entries": 400,
	"unsafe_archive": 400,
	"pack_too_large_extracted": 413,
	"headers_failed": 422,
	"timeout": 504,
}
""" Status for each way a headers pass can fail, so the page can tell a bad upload from an outage. """

SLOT: threading.BoundedSemaphore = threading.BoundedSemaphore(1)
""" One job at a time: the container is sized for a single child. """


# Classes
class Handler(BaseHTTPRequestHandler):
	""" POST /build, POST /headers, GET /health, GET /textures. Nothing else exists. """

	protocol_version: str = "HTTP/1.1"

	def log_message(self, format: str, *args: Any) -> None:
		""" Silence the default per request logging, which says nothing the caller does not know.

		Args:
			format (str): Unused, part of the BaseHTTPRequestHandler protocol.
			args   (Any): Unused, part of the BaseHTTPRequestHandler protocol.
		"""
		return

	def reply(self, status: int, payload: dict[str, Any]) -> None:
		""" Send one JSON response.

		Args:
			status  (int):             HTTP status code.
			payload (dict[str, Any]):  Body to serialize.
		"""
		self.send_bytes(status, "application/json; charset=utf-8", json.dumps(payload).encode("utf-8"))

	def reply_archive(self, archive: bytes, counts: dict[str, Any], warnings: list[str]) -> None:
		""" Send a rewritten pack, with the little that does not fit in a zip carried in a header.

		Warnings are the only unbounded part, so they are what gets dropped, last one first, until the
		header fits. Dropping them silently would be worse than saying how many went, so the count
		travels with what is left.

		Args:
			archive  (bytes):          The archive to hand back.
			counts   (dict[str, Any]): Duration and the function counts, always small enough to fit.
			warnings (list[str]):      What the analysis warned about, trimmed to fit the ceiling.
		"""
		kept: list[str] = warnings[:MAX_WARNINGS]
		dropped: int = len(warnings) - len(kept)
		while True:
			meta: dict[str, Any] = counts | {"warnings": kept} | ({"warningsDropped": dropped} if dropped else {})
			encoded: str = base64.b64encode(json.dumps(meta).encode("utf-8")).decode("ascii")
			if len(encoded) <= MAX_META_CHARS or not kept:
				break
			kept = kept[:-1]
			dropped += 1

		self.send_bytes(200, "application/zip", archive, {META_HEADER: encoded})

	def send_bytes(self, status: int, content_type: str, body: bytes, headers: dict[str, str] | None = None) -> None:
		""" Send one response with an explicit length, so keep-alive stays honest.

		Args:
			status       (int):              HTTP status code.
			content_type (str):              Value of the Content-Type header.
			body         (bytes):            Response body.
			headers      (dict[str, str]):   Anything else to send.
		"""
		self.send_response(status)
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", str(len(body)))
		for name, value in (headers or {}).items():
			self.send_header(name, value)
		self.end_headers()
		self.wfile.write(body)

	def do_GET(self) -> None:
		""" Health and the bundled texture listing. """
		if self.path == "/health":
			self.reply(200, {"ok": True})
		elif self.path == "/textures":
			try:
				with open(f"{SRV}/assets/textures.json", encoding="utf-8") as file:
					self.reply(200, {"ok": True, "textures": json.load(file)})
			except OSError:
				self.reply(200, {"ok": True, "textures": []})
		else:
			self.reply(404, {"ok": False, "error": "not_found"})

	def do_POST(self) -> None:
		""" Run one job, one at a time. """
		if self.path == "/build":
			self.do_build()
		elif self.path == "/headers":
			self.do_headers()
		else:
			self.reply(404, {"ok": False, "error": "not_found"})

	def do_build(self) -> None:
		""" Build a submitted definitions module. """
		length: int = int(self.headers.get("Content-Length") or 0)
		if length > MAX_CODE_BYTES * 2:
			self.reply(400, {"ok": False, "error": "code_too_large"})
			return

		try:
			code: str = str(json.loads(self.rfile.read(length) or b"{}").get("code", ""))
		except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
			self.reply(400, {"ok": False, "error": "invalid_body"})
			return

		if not code.strip():
			self.reply(400, {"ok": False, "error": "invalid_body"})
			return
		if len(code.encode("utf-8")) > MAX_CODE_BYTES:
			self.reply(400, {"ok": False, "error": "code_too_large"})
			return
		if not self.take_slot(MIN_FREE_BYTES):
			return

		try:
			self.reply(200, Build.run(code))
		finally:
			SLOT.release()

	def do_headers(self) -> None:
		""" Run auto.headers over an uploaded pack and hand the rewritten archive straight back. """
		length: int = int(self.headers.get("Content-Length") or 0)
		if length > MAX_PACK_BYTES:
			self.reply(413, {"ok": False, "error": "pack_too_large"})
			return
		if length == 0:
			self.reply(400, {"ok": False, "error": "invalid_body"})
			return

		pack: bytes = self.rfile.read(length)
		if not self.take_slot(MIN_HEADERS_FREE_BYTES):
			return

		try:
			payload, archive = Headers.run(pack)
			if payload.get("ok") is not True:
				self.reply(HEADERS_STATUS.get(str(payload.get("error")), 500), payload)
				return
			self.reply_archive(
				archive,
				{key: payload.get(key) for key in ("durationMs", "functions", "changed")},
				Job.warnings(str(payload.get("logs", ""))),
			)
		finally:
			SLOT.release()

	def take_slot(self, min_free: int) -> bool:
		""" Check the scratch space and take the single job slot, answering the caller when it cannot.

		Args:
			min_free (int): How much room /tmp must have before the job is worth starting.
		Returns:
			bool: Whether the slot is now held, in which case the caller must release it.
		"""
		if shutil.disk_usage("/tmp").free < min_free:
			self.reply(503, {"ok": False, "error": "no_scratch_space"})
			return False
		if not SLOT.acquire(timeout=QUEUE_TIMEOUT):
			self.reply(503, {"ok": False, "error": "busy"})
			return False
		return True


# Functions
def main() -> int:
	""" Serve until killed, or run the selftest and exit.

	Returns:
		int: Process exit code.
	"""
	if "--selftest" in sys.argv:
		return selftest()

	print(f"Sandbox worker listening on 0.0.0.0:{PORT}", flush=True)
	ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
	return 0


if __name__ == "__main__":
	sys.exit(main())

