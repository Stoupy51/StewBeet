""" Anonymous build telemetry: one counter increment per successful StewBeet build.

The whole feature lives in this file so anyone can read it in less than a minute and know exactly what
leaves their machine: the StewBeet version, the full Python version (major.minor.micro), and how long
the build took. Nothing identifies the project, the machine or the person, and nothing is stored
between builds.

Set ``STEWBEET_TELEMETRY=0`` to turn it off, every failure is swallowed:
a build never fails, slows down or changes because of it.

Public page and aggregated numbers: https://stewbeet.paralya.fr/telemetry
"""
# Imports
import json
import os
import sys
import threading
import urllib.request

from stouputils.typing import JsonDict

# Constants
ENDPOINT: str = "https://stewbeet.paralya.fr/api/telemetry/build"
""" Where the event goes. The server keeps a daily counter and forgets everything else. """

OPT_OUT_VARIABLE: str = "STEWBEET_TELEMETRY"
""" Setting this to 0 (or false/no/off) disables telemetry entirely. """

TIMEOUT_SECONDS: float = 2.0
""" Connect plus read budget. Short on purpose: an unreachable server must not hold a build open. """

DISABLED_VALUES: frozenset[str] = frozenset({"0", "false", "no", "off"})
""" Values of STEWBEET_TELEMETRY that mean "do not send anything". """


# Classes
class Telemetry:
	""" The only entry point is `Telemetry.record_build`, called once a build has succeeded. """

	@staticmethod
	def is_enabled() -> bool:
		""" Whether telemetry may be sent at all.

		Returns:
			bool: True unless STEWBEET_TELEMETRY names one of the disabled values.

		Examples:
			>>> os.environ[OPT_OUT_VARIABLE] = "0"
			>>> Telemetry.is_enabled()
			False
			>>> os.environ[OPT_OUT_VARIABLE] = "1"
			>>> Telemetry.is_enabled()
			True
			>>> del os.environ[OPT_OUT_VARIABLE]
			>>> Telemetry.is_enabled()
			True
		"""
		return os.environ.get(OPT_OUT_VARIABLE, "1").strip().lower() not in DISABLED_VALUES

	@staticmethod
	def stewbeet_version() -> str:
		""" Installed StewBeet version, or "unknown" when the package metadata is not there. """
		from importlib.metadata import PackageNotFoundError, version
		try:
			return version("stewbeet")
		except PackageNotFoundError:
			return "unknown"

	@staticmethod
	def payload(duration_seconds: float) -> JsonDict:
		""" The complete body of the request. These three keys are all there has ever been.

		Args:
			duration_seconds (float): How long the build took, in seconds.
		Returns:
			JsonDict: The documented fields, and nothing else.

		Examples:
			>>> sorted(Telemetry.payload(1.2345))
			['duration_seconds', 'python_version', 'stewbeet_version']
			>>> Telemetry.payload(1.2345)["duration_seconds"]
			1.234
			>>> Telemetry.payload(-1.0)["duration_seconds"]
			0.0
		"""
		return {
			"stewbeet_version": Telemetry.stewbeet_version(),
			"python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
			"duration_seconds": round(max(duration_seconds, 0.0), 3),
		}

	@staticmethod
	def send(payload: JsonDict) -> None:
		""" POST one event and drop the answer, along with any error it took to get there.

		Args:
			payload (JsonDict): The body built by `Telemetry.payload`.
		"""
		request = urllib.request.Request(
			ENDPOINT,
			data=json.dumps(payload).encode("utf-8"),
			headers={"Content-Type": "application/json", "User-Agent": "stewbeet-telemetry"},
			method="POST",
		)
		try:
			urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS).close()
		except Exception:
			pass

	@staticmethod
	def record_build(duration_seconds: float) -> threading.Thread | None:
		""" Report one successful build, on a thread so the terminal gets its prompt back immediately.

		The thread is not a daemon, so the interpreter waits for it on the way out, and
		`TIMEOUT_SECONDS` is what bounds that wait.

		Args:
			duration_seconds (float): How long the build took, in seconds.
		Returns:
			threading.Thread | None: The delivery thread, or None when telemetry is disabled.

		Examples:
			>>> sent: list[JsonDict] = []
			>>> original = Telemetry.send
			>>> Telemetry.send = staticmethod(sent.append)

			A successful build sends exactly one event, carrying only the documented fields:

			>>> Telemetry.record_build(0.5).join()
			>>> len(sent)
			1
			>>> sorted(sent[0])
			['duration_seconds', 'python_version', 'stewbeet_version']

			Opting out sends nothing at all:

			>>> os.environ[OPT_OUT_VARIABLE] = "0"
			>>> print(Telemetry.record_build(0.5))
			None
			>>> len(sent)
			1
			>>> del os.environ[OPT_OUT_VARIABLE]

			A delivery that blows up is still not the build's problem:

			>>> def explode(payload: JsonDict) -> None:
			...     raise ConnectionError("server is down")
			>>> Telemetry.send = staticmethod(explode)
			>>> Telemetry.record_build(0.5).join()
			>>> Telemetry.send = original
		"""
		if not Telemetry.is_enabled():
			return None

		def deliver() -> None:
			try:
				Telemetry.send(Telemetry.payload(duration_seconds))
			except Exception:
				pass

		thread = threading.Thread(target=deliver, name="stewbeet-telemetry")
		thread.start()
		return thread

