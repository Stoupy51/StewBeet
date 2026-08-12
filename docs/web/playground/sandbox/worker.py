""" HTTP front of the playground sandbox: one build at a time, each in a throwaway process.

Deliberately stdlib only, and it never imports stewbeet. The worker has to outlive every way a
build can die, so it stays a few megabytes of interpreter that cannot be broken by anything the
build does to its own address space.

The container is the security boundary, not this file: `internal: true` networking, `read_only`
rootfs, `cap_drop: ALL` and the memory cgroup are what make running submitted Python acceptable.
What is here is the second layer, so that one abusive request degrades into an error message
instead of into an outage for the next visitor.
"""
# Imports
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

# Constants
SRV: str = "/srv"
""" Image root holding project/, runner.py and the bundled assets. """

PORT: int = 8000
""" Only ever reached over the internal compose network, never published to the host. """

MAX_CODE_BYTES: int = 16 * 1024
""" Also enforced on the web side. Repeated here because the worker cannot assume its caller. """

MAX_LOG_CHARS: int = 64 * 1024
""" Tail of the build log kept for the UI. beet and stouputils are talkative. """

WALL_TIMEOUT: float = 20.0
""" Wall clock ceiling for one build. RLIMIT_CPU fires first for a busy loop; this covers sleep. """

QUEUE_TIMEOUT: float = 2.0
""" How long a request waits for the single build slot before being told to come back. """

MIN_FREE_BYTES: int = 32 * 1024 * 1024
""" Refuse to start a build when /tmp has less room than this, rather than failing halfway. """

SENTINEL: str = "===STEWBEET-RESULT==="
""" Line after which the child's stdout is the JSON payload and nothing else. """

ANSI: re.Pattern[str] = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
""" stouputils colours its output, and the UI shows the log as plain text. """

SLOT: threading.BoundedSemaphore = threading.BoundedSemaphore(1)
""" One build at a time: the container is sized for a single 512 MiB child. """


# Classes
class Rlimits:
	""" Per process ceilings, applied between fork and exec.

	These are the inner layer. The memory cgroup is the hard one, but a cgroup OOM kill takes an
	arbitrary process in the container, which could be the worker itself. A process that exceeds
	RLIMIT_AS instead gets a MemoryError inside its own build, which is both survivable and
	reportable.
	"""

	ADDRESS_SPACE: int = 512 * 1024 * 1024
	""" Roughly 7x the 68.5 MB peak measured on a real project. """

	CPU_SECONDS: int = 10
	""" Roughly 18x the 0.54 s measured on a real project. """

	FILE_SIZE: int = 16 * 1024 * 1024
	""" One write of a gigabyte dies with SIGXFSZ instead of filling the shared tmpfs. """

	OPEN_FILES: int = 256
	""" Enough for beet's own file handling, far short of exhausting the container. """

	@staticmethod
	def apply() -> None:
		""" Set every limit on the calling process, and start a new session.

		The new session matters as much as the limits: it gives the child its own process group, so
		a timeout can kill everything it spawned rather than only the process that was waited on.

		RLIMIT_NPROC is deliberately absent. It counts processes per uid, not per process, so with
		one shared uid a fork bomb in one request would deny service to every later request and to
		the worker's own threads. The container's pids_limit covers that case without the
		collateral damage.
		"""
		resource.setrlimit(resource.RLIMIT_AS, (Rlimits.ADDRESS_SPACE, Rlimits.ADDRESS_SPACE))
		resource.setrlimit(resource.RLIMIT_CPU, (Rlimits.CPU_SECONDS, Rlimits.CPU_SECONDS))
		resource.setrlimit(resource.RLIMIT_FSIZE, (Rlimits.FILE_SIZE, Rlimits.FILE_SIZE))
		resource.setrlimit(resource.RLIMIT_NOFILE, (Rlimits.OPEN_FILES, Rlimits.OPEN_FILES))
		resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
		os.setsid()


class Build:
	""" One submitted build, from throwaway directory to parsed payload. """

	@staticmethod
	def environment(workdir: str) -> dict[str, str]:
		""" Minimal environment, with every writable path pointed inside the throwaway directory.

		Args:
			workdir (str): The per request directory, which is deleted afterwards.
		Returns:
			dict[str, str]: Environment for the child process.
		"""
		return {
			"PATH": "/usr/bin:/bin",
			"HOME": workdir,
			"TMPDIR": workdir,
			"XDG_CACHE_HOME": f"{workdir}/cache",
			# The rootfs is read only and the tmpfs is a shared budget: neither wants __pycache__.
			"PYTHONDONTWRITEBYTECODE": "1",
			"PYTHONUNBUFFERED": "1",
			"PYTHONHASHSEED": "0",
			"LANG": "C.UTF-8",
			"LC_ALL": "C.UTF-8",
			"NO_COLOR": "1",
		}

	@staticmethod
	def sweep() -> None:
		""" Empty /tmp before a build starts.

		Pointing the child's TMPDIR at its own throwaway directory only redirects code that asks
		politely. Nothing stops submitted code from writing to /tmp directly, and those files
		outlive the request that made them, so without this the shared 128 MB tmpfs would fill up
		one visitor at a time until every build failed on scratch space.

		Safe to do unconditionally because the caller holds the single build slot, so no other build
		owns anything under /tmp at this point.
		"""
		for name in os.listdir("/tmp"):
			path: str = f"/tmp/{name}"
			if os.path.isdir(path) and not os.path.islink(path):
				shutil.rmtree(path, ignore_errors=True)
			else:
				try:
					os.unlink(path)
				except OSError:
					pass

	@staticmethod
	def link_assets(workdir: str) -> None:
		""" Give the build writable texture and render folders backed by the bundled ones.

		Both have to be writable, because src.placeholders adds a texture for every id the bundled
		packs do not cover and seeds a render for every definition, and the image is read only.
		Copying instead would spend a quarter of the 128 MB tmpfs per request on bytes that are
		identical every time, so the build gets links: a few hundred inodes, no data, and the
		rglob("*.png") on the other side cannot tell the difference.

		Textures are linked file by file, since placeholders land beside them in the same folder.
		Renders are linked one namespace at a time, since a placeholder render goes into the
		project's own namespace, which no bundled pack provides.

		Args:
			workdir (str): The per request directory, which beet.yml reads as `../textures` and
				`../iso_renders` from the project beside it.
		"""
		textures: str = f"{workdir}/textures"
		os.makedirs(textures, exist_ok=True)
		for entry in os.scandir(f"{SRV}/assets/textures"):
			if entry.is_file():
				os.symlink(entry.path, f"{textures}/{entry.name}")

		renders: str = f"{workdir}/iso_renders"
		os.makedirs(renders, exist_ok=True)
		for entry in os.scandir(f"{SRV}/assets/iso_renders"):
			if entry.is_dir():
				os.symlink(entry.path, f"{renders}/{entry.name}")

	@staticmethod
	def prepare(code: str) -> str:
		""" Lay out a fresh directory for one build and drop the submitted code into it.

		Args:
			code (str): The submitted definitions module.
		Returns:
			str: Path of the new directory, which the caller must delete.
		"""
		workdir: str = tempfile.mkdtemp(dir="/tmp", prefix="build-")
		project: str = f"{workdir}/project"
		shutil.copytree(f"{SRV}/project", project)
		os.makedirs(f"{workdir}/cache", exist_ok=True)
		# beet.yml reads ../textures and ../iso_renders, so these sit beside the project.
		Build.link_assets(workdir)
		with open(f"{project}/src/user_code.py", "w", encoding="utf-8", newline="\n") as file:
			file.write(code)
		return workdir

	@staticmethod
	def launch(project: str, workdir: str) -> tuple[str, bool]:
		""" Run runner.py against the project and return its stdout.

		The child is killed by process group, twice: once when the wait times out, and again in the
		finally, because a child that exited normally may still have left grandchildren behind.

		Args:
			project (str): Directory holding beet.yml and src/.
			workdir (str): The per request directory, used as the child's home and temp.
		Returns:
			tuple[str, bool]: The child's combined output, and whether it timed out.
		"""
		process: subprocess.Popen[str] = subprocess.Popen(
			[f"{SRV}/.venv/bin/python", f"{SRV}/runner.py", project],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			stdin=subprocess.DEVNULL,
			cwd=project,
			env=Build.environment(workdir),
			text=True,
			errors="replace",
			preexec_fn=Rlimits.apply,
		)
		try:
			output, _ = process.communicate(timeout=WALL_TIMEOUT)
			return output, False
		except subprocess.TimeoutExpired:
			Build.kill(process)
			output, _ = process.communicate()
			return output, True
		finally:
			Build.kill(process)

	@staticmethod
	def kill(process: subprocess.Popen[str]) -> None:
		""" SIGKILL the child's whole process group, ignoring a group that is already gone.

		Args:
			process (subprocess.Popen[str]): The child to kill.
		"""
		try:
			os.killpg(os.getpgid(process.pid), signal.SIGKILL)
		except (ProcessLookupError, PermissionError):
			pass

	@staticmethod
	def parse(output: str, timed_out: bool) -> dict[str, Any]:
		""" Split the child's stdout into build log and JSON payload.

		A missing sentinel means the child died before it could report, which is what an OOM kill,
		a SIGXFSZ or a SIGKILL look like from here.

		Args:
			output    (str):  Everything the child printed.
			timed_out (bool): Whether the wall clock ceiling was reached.
		Returns:
			dict[str, Any]: The payload, always carrying `ok` and `logs`.
		"""
		head, found, tail = output.rpartition(f"{SENTINEL}\n")
		logs: str = ANSI.sub("", head if found else output)[-MAX_LOG_CHARS:]

		if timed_out:
			return {"ok": False, "error": "timeout", "logs": logs}
		if not found:
			return {"ok": False, "error": "crashed", "logs": logs}
		try:
			return dict(json.loads(tail)) | {"logs": logs}
		except json.JSONDecodeError:
			return {"ok": False, "error": "crashed", "logs": logs}

	@staticmethod
	def run(code: str) -> dict[str, Any]:
		""" Prepare, build and clean up, whatever happens in between.

		Args:
			code (str): The submitted definitions module.
		Returns:
			dict[str, Any]: The payload, with the build duration added.
		"""
		started: float = time.monotonic()
		Build.sweep()
		workdir: str = Build.prepare(code)
		try:
			output, timed_out = Build.launch(f"{workdir}/project", workdir)
			return Build.parse(output, timed_out) | {"durationMs": round((time.monotonic() - started) * 1000)}
		finally:
			# The tmpfs is a shared budget and it is the only writable place in the container: a
			# directory leaked here is taken away from every request that follows.
			shutil.rmtree(workdir, ignore_errors=True)


class Handler(BaseHTTPRequestHandler):
	""" POST /build, GET /health, GET /textures. Nothing else exists. """

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
		body: bytes = json.dumps(payload).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json; charset=utf-8")
		self.send_header("Content-Length", str(len(body)))
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
		""" Build the submitted code, one at a time. """
		if self.path != "/build":
			self.reply(404, {"ok": False, "error": "not_found"})
			return

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
		if shutil.disk_usage("/tmp").free < MIN_FREE_BYTES:
			self.reply(503, {"ok": False, "error": "no_scratch_space"})
			return
		if not SLOT.acquire(timeout=QUEUE_TIMEOUT):
			self.reply(503, {"ok": False, "error": "busy"})
			return

		try:
			self.reply(200, Build.run(code))
		finally:
			SLOT.release()


# Functions
def selftest() -> int:
	""" Build at image build time, so a broken pipeline fails the image and not a visitor.

	The render node is the case that matters. auto.text_renders reaches model_resolver, and the
	OpenGL context this container has no display for, for any item with no cached render:
	emit.source_images -> ensure_item_images -> run_model_resolver. src.placeholders is what keeps
	that queue empty, and this is what notices the day it stops working.

	Returns:
		int: 0 when every build succeeded.
	"""
	template: str = (
		"from beet import Context\n"
		"from stewbeet import *\n"
		"\n"
		"\n"
		"def beet_default(ctx: Context):\n"
		'    Item(id="{item}", components={{"item_name": {{"text": "Selftest"}}{lore}}})\n'
		"    add_item_model_component()\n"
	)
	render: str = ', "lore": [[{"render": "steel_ingot"}]]'
	cases: dict[str, str] = {
		"bundled texture": template.format(item="steel_ingot", lore=""),
		"no texture at all": template.format(item="zzz_nothing_has_this_name", lore=""),
		"a render node": template.format(item="steel_ingot", lore=render),
	}
	failed: bool = False
	for name, code in cases.items():
		result: dict[str, Any] = Build.run(code)
		count: int = len(result.get("files", []))
		if result.get("ok") and count > 0:
			print(f"selftest: {name}: {count} files in {result.get('durationMs')} ms")
		else:
			failed = True
			print(f"selftest: {name}: FAILED ({result.get('error')})\n{result.get('logs', '')[-4000:]}")
	return 1 if failed else 0


def main() -> int:
	""" Serve until killed, or run the selftest and exit.

	Returns:
		int: Process exit code.
	"""
	if "--selftest" in sys.argv:
		return selftest()

	print(f"Playground worker listening on 0.0.0.0:{PORT}", flush=True)
	ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
	return 0


if __name__ == "__main__":
	sys.exit(main())
