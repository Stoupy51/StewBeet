""" Containment tests for the playground sandbox, run against a container that is already up.

    docker build -t stewbeet-playground docs/web/playground/sandbox
    docker run -d --name pg --network none --read-only \
      --tmpfs /tmp:rw,noexec,nosuid,nodev,size=128m,mode=1777 \
      --memory 1g --memory-swap 1g --cpus 1 --pids-limit 96 \
      --cap-drop ALL --security-opt no-new-privileges:true \
      -p 127.0.0.1:8001:8000 stewbeet-playground
    python docs/web/playground/sandbox/tests/test_sandbox.py http://127.0.0.1:8001

Every case submits code that probes one thing and prints what happened, then asserts on the build
log. The container has to survive all of it: a case that passes while leaving the service dead is a
failing run, which is why the last thing this does is build normally one more time.

Stdlib only, so it runs with any interpreter, including the one inside the image.
"""
# Imports
import json
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

# Constants
TIMEOUT: float = 60.0
""" Generous: a case that deliberately runs into the 20 s wall clock ceiling still has to return. """

PREAMBLE: str = "from beet import Context\nfrom stewbeet import *\n\n\ndef beet_default(ctx: Context):\n"
""" Every probe is a definitions module, because that is the only shape the pipeline accepts. """


# Classes
@dataclass(frozen=True)
class Case:
	""" One probe and what the response has to look like. """

	name: str
	""" Shown in the report. """

	body: str
	""" Statements placed inside beet_default, dedented. """

	ok: bool | None = None
	""" Required value of the response's `ok`, or None when either outcome is acceptable. """

	error: str | None = None
	""" Required value of the response's `error`. """

	contains: tuple[str, ...] = ()
	""" Substrings that must all appear somewhere in the response. """

	absent: tuple[str, ...] = ()
	""" Substrings that must not appear anywhere in the response. This is where a leak shows up. """


@dataclass
class Report:
	""" Running tally across the whole file. """

	passed: int = 0
	failures: list[str] = field(default_factory=list)

	def check(self, name: str, condition: bool, detail: str = "") -> None:
		""" Record one assertion.

		Args:
			name      (str):  Case name.
			condition (bool): Whether it held.
			detail    (str):  Shown when it did not.
		"""
		if condition:
			self.passed += 1
			print(f"  ok    {name}")
		else:
			self.failures.append(f"{name}: {detail}")
			print(f"  FAIL  {name}: {detail}")


# Functions
def post(base: str, code: str) -> dict[str, Any]:
	""" Submit code to the worker and return the parsed response.

	Args:
		base (str): Worker base URL, ex: "http://127.0.0.1:8001".
		code (str): The definitions module to build.
	Returns:
		dict[str, Any]: The response body, with the HTTP status added as `status`.
	"""
	request: urllib.request.Request = urllib.request.Request(
		f"{base}/build",
		data=json.dumps({"code": code}).encode("utf-8"),
		headers={"Content-Type": "application/json"},
		method="POST",
	)
	try:
		with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
			return dict(json.load(response)) | {"status": response.status}
	except urllib.error.HTTPError as error:
		return dict(json.loads(error.read() or b"{}")) | {"status": error.code}
	except OSError as error:
		# A dropped connection is a finding, not a reason to abandon the run: it is what a worker
		# that has run out of pids or threads looks like from here, and the cases after this one are
		# the ones that say whether it ever recovers.
		return {"ok": None, "error": f"no_response: {type(error).__name__}: {error}", "status": 0}


def probe(body: str) -> str:
	""" Wrap probe statements into a definitions module.

	Args:
		body (str): Statements to run, dedented.
	Returns:
		str: A complete module the pipeline can import.
	"""
	return PREAMBLE + textwrap.indent(textwrap.dedent(body).strip() + "\n", "    ")


def cases() -> list[Case]:
	""" Every containment case, in the order they have to run.

	The /tmp pair is order dependent: the second case only proves anything because the first one
	wrote the file it looks for.

	Returns:
		list[Case]: The cases.
	"""
	return [
		Case(
			name="a normal build succeeds",
			body='Item(id="steel_ingot", components={"item_name": {"text": "Steel"}})\nadd_item_model_component()',
			ok=True,
		),

		# ── Disk ──────────────────────────────────────────────────────────────────────────────
		# The three probes below print PROBE:REFUSED rather than the exception's class name, because
		# the class is not the point and asserting on it is how this test was wrong twice. EROFS and
		# EACCES both arrive as OSError subclasses, and which one you get depends on whether the
		# permission check or the read-only check answers first: every path on the rootfs is root
		# owned and mode 644, and the build runs as uid 10001, so in practice it is EACCES. Nothing
		# outside /tmp being writable is the property that matters, and it holds either way.
		Case(
			name="the image is not writable",
			body='''
			try:
				open("/srv/runner.py", "a")
				print("PROBE:WRITABLE")
			except OSError as error:
				print(f"PROBE:REFUSED:{error.errno}:{type(error).__name__}")
			''',
			contains=("PROBE:REFUSED:",),
			absent=("PROBE:WRITABLE",),
		),
		Case(
			name="/etc is not writable",
			body='''
			try:
				open("/etc/passwd", "a")
				print("PROBE:WRITABLE")
			except OSError as error:
				print(f"PROBE:REFUSED:{error.errno}:{type(error).__name__}")
			''',
			contains=("PROBE:REFUSED:",),
			absent=("PROBE:WRITABLE",),
		),
		Case(
			name="/proc/sysrq-trigger is refused",
			body='''
			try:
				open("/proc/sysrq-trigger", "w")
				print("PROBE:WRITABLE")
			except OSError as error:
				print(f"PROBE:REFUSED:{error.errno}:{type(error).__name__}")
			''',
			contains=("PROBE:REFUSED:",),
			absent=("PROBE:WRITABLE",),
		),
		Case(
			name="there is no docker socket",
			body='''
			try:
				open("/var/run/docker.sock")
				print("PROBE:PRESENT")
			except OSError as error:
				print(f"PROBE:{type(error).__name__}")
			''',
			contains=("PROBE:FileNotFoundError",),
			absent=("PROBE:PRESENT",),
		),
		Case(
			name="/tmp is writable",
			body='''
			open("/tmp/leaked-marker", "w").write("x")
			print("PROBE:WROTE")
			''',
			contains=("PROBE:WROTE",),
		),
		Case(
			name="/tmp is swept between builds",
			body='''
			import os
			print("PROBE:PRESENT" if os.path.exists("/tmp/leaked-marker") else "PROBE:GONE")
			''',
			contains=("PROBE:GONE",),
			absent=("PROBE:PRESENT",),
		),
		Case(
			name="/tmp is noexec",
			body='''
			import os, subprocess
			open("/tmp/run.sh", "w").write("#!/bin/sh\\necho PROBE:EXECUTED\\n")
			os.chmod("/tmp/run.sh", 0o755)
			try:
				subprocess.run(["/tmp/run.sh"], check=False, capture_output=True)
				print("PROBE:SPAWNED")
			except OSError as error:
				print(f"PROBE:{type(error).__name__}")
			''',
			contains=("PROBE:PermissionError",),
			absent=("PROBE:EXECUTED",),
		),
		Case(
			name="a single huge file hits RLIMIT_FSIZE",
			body='''
			with open("/tmp/huge", "wb") as handle:
				for _ in range(100):
					handle.write(b"x" * (1024 * 1024))
			print("PROBE:WROTE100MB")
			''',
			ok=False,
			absent=("PROBE:WROTE100MB",),
		),

		# ── Memory ────────────────────────────────────────────────────────────────────────────
		Case(
			name="a 2 GB allocation hits RLIMIT_AS, not the container",
			body='bytearray(2 * 1024 ** 3)\nprint("PROBE:ALLOCATED")',
			ok=False,
			contains=("MemoryError",),
			absent=("PROBE:ALLOCATED",),
		),

		# ── Network ───────────────────────────────────────────────────────────────────────────
		Case(
			name="there is no route out",
			body='''
			import socket
			try:
				socket.create_connection(("1.1.1.1", 53), 3)
				print("PROBE:CONNECTED")
			except OSError as error:
				print(f"PROBE:{type(error).__name__}")
			''',
			absent=("PROBE:CONNECTED",),
		),
		Case(
			name="there is no DNS",
			body='''
			import socket
			try:
				print(f"PROBE:RESOLVED:{socket.gethostbyname('pypi.org')}")
			except OSError as error:
				print(f"PROBE:{type(error).__name__}")
			''',
			absent=("PROBE:RESOLVED",),
		),
		Case(
			name="http out fails",
			body='''
			import urllib.request
			try:
				urllib.request.urlopen("http://example.com", timeout=5)
				print("PROBE:FETCHED")
			except Exception as error:
				print(f"PROBE:{type(error).__name__}")
			''',
			absent=("PROBE:FETCHED",),
		),

		# ── Process ───────────────────────────────────────────────────────────────────────────
		Case(
			name="an infinite loop is killed",
			body="while True:\n    pass",
			ok=False,
		),
		Case(
			name="a fork bomb is contained",
			body='''
			import os
			while True:
				try:
					os.fork()
				except OSError:
					pass
			''',
			ok=False,
		),
		Case(
			# The case that matters, and the one that caught the zombie leak: containing the fork
			# bomb is worthless if the worker cannot answer afterwards. It could not, until
			# `init: true` and Build.reap, because orphans reparented to PID 1 sat as zombies
			# holding pids until the worker could no longer spawn a thread for a new connection.
			name="the service still answers after a fork bomb",
			body='Item(id="steel_ingot", components={"item_name": {"text": "Steel"}})\nadd_item_model_component()',
			ok=True,
		),

		# ── No GPU ────────────────────────────────────────────────────────────────────────────
		Case(
			name="a made up item id gets a placeholder instead of failing",
			body='Item(id="zzz_nothing_has_this_name", components={"item_name": {"text": "Nothing"}})\nadd_item_model_component()',
			ok=True,
			contains=("No bundled texture for zzz_nothing_has_this_name",),
			absent=("model_resolver.render",),
		),
		Case(
			name="a render node makes a glyph with no GPU",
			# The case that proves seeding the render cache works. Without src.placeholders this
			# reaches emit.source_images -> ensure_item_images -> run_model_resolver -> OpenGL.
			body='''
			Item(id="steel_ingot", components={"item_name": {"text": "Steel"},
				"lore": [[{"render": "steel_ingot"}, {"text": " ingot"}]]})
			add_item_model_component()
			''',
			ok=True,
			contains=("textures/font/renders/",),
			absent=("model_resolver.render",),
		),
		Case(
			name="importing model_resolver.render is blocked",
			body='''
			try:
				import model_resolver.render
				print("PROBE:IMPORTED")
			except ImportError as error:
				print(f"PROBE:ImportError:{error}")
			''',
			contains=("PROBE:ImportError",),
			absent=("PROBE:IMPORTED",),
		),
	]


def run_cases(base: str, report: Report) -> None:
	""" Submit every case and check its response.

	Args:
		base   (str):    Worker base URL.
		report (Report): Tally to record into.
	"""
	for case in cases():
		response: dict[str, Any] = post(base, probe(case.body))
		blob: str = json.dumps(response)

		if case.ok is not None:
			report.check(f"{case.name} [ok is {case.ok}]", response.get("ok") is case.ok, f"got {response.get('ok')} / {response.get('error')}")
		if case.error is not None:
			report.check(f"{case.name} [error]", response.get("error") == case.error, f"got {response.get('error')}")
		for needle in case.contains:
			report.check(f"{case.name} [has {needle!r}]", needle in blob, "not found in the response")
		for needle in case.absent:
			report.check(f"{case.name} [no {needle!r}]", needle not in blob, "PRESENT IN THE RESPONSE")


def run_protocol(base: str, report: Report) -> None:
	""" Check the cases that are about the request rather than about the build.

	Args:
		base   (str):    Worker base URL.
		report (Report): Tally to record into.
	"""
	oversized: dict[str, Any] = post(base, PREAMBLE + "    pass\n" + "#" * (17 * 1024))
	report.check("oversized code is refused", oversized.get("error") == "code_too_large", f"got {oversized.get('error')}")

	empty: dict[str, Any] = post(base, "   ")
	report.check("empty code is refused", empty.get("error") == "invalid_body", f"got {empty.get('error')}")

	with urllib.request.urlopen(f"{base}/health", timeout=TIMEOUT) as response:
		report.check("the worker is still healthy", response.status == 200, f"got {response.status}")

	survivor: dict[str, Any] = post(base, probe('Item(id="steel_ingot", components={"item_name": {"text": "Steel"}})\nadd_item_model_component()'))
	report.check("a normal build still works at the end", survivor.get("ok") is True, f"got {survivor.get('error')}")


def main() -> int:
	""" Run everything against the worker named on the command line.

	Returns:
		int: 0 when every check passed.
	"""
	if len(sys.argv) != 2:
		print("usage: test_sandbox.py <worker base url>")
		return 2

	base: str = sys.argv[1].rstrip("/")
	report: Report = Report()

	print("Containment:")
	run_cases(base, report)
	print("Protocol:")
	run_protocol(base, report)

	print(f"\n{report.passed} passed, {len(report.failures)} failed")
	for failure in report.failures:
		print(f"  {failure}")
	return 1 if report.failures else 0


if __name__ == "__main__":
	sys.exit(main())
