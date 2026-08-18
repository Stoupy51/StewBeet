""" What both sandbox jobs share: the per process ceilings, the throwaway directory and the kill path.

Deliberately stdlib only, and it never imports stewbeet. The worker has to outlive every way a job
can die, so it stays a few megabytes of interpreter that cannot be broken by anything the child does
to its own address space.

The container is the security boundary, not this file: `internal: true` networking, `read_only`
rootfs, `cap_drop: ALL` and the memory cgroup are what make running submitted code acceptable. What
is here is the second layer, so that one abusive request degrades into an error message instead of
into an outage for the next visitor.
"""
# Imports
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Any

# Constants
SRV: str = "/srv"
""" Image root holding project/, the runners and the bundled assets. """

MAX_LOG_CHARS: int = 64 * 1024
""" Tail of the build log kept for the UI. beet and stouputils are talkative. """

KILL_GRACE: float = 3.0
""" How long to keep signalling a process group, and to wait for its output afterwards. """

KILL_INTERVAL: float = 0.05
""" Gap between signals. Short enough to outpace a fork loop, long enough not to spin. """

SENTINEL: str = "===STEWBEET-RESULT==="
""" Line after which the child's stdout is the JSON payload and nothing else. """

ANSI: re.Pattern[str] = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
""" stouputils colours its output, and the UI shows the log as plain text. """

WARNING_PREFIX: str = "[WARNING"
""" How stouputils opens a warning line, which is how one is told apart from the rest of the log. """


# Classes
@dataclass(frozen=True)
class Rlimits:
	""" Per process ceilings, applied between fork and exec.

	These are the inner layer. The memory cgroup is the hard one, but a cgroup OOM kill takes an
	arbitrary process in the container, which could be the worker itself. A process that exceeds
	RLIMIT_AS instead gets a MemoryError inside its own job, which is both survivable and reportable.

	RLIMIT_NPROC is deliberately absent. It counts processes per uid, not per process, so with one
	shared uid a fork bomb in one request would deny service to every later request and to the
	worker's own threads. The container's pids_limit covers that case without the collateral damage.
	"""

	address_space: int
	""" Ceiling on the child's virtual memory, well above what a real project measures. """

	cpu_seconds: int
	""" Ceiling on CPU time, which is what catches a busy loop before the wall clock does. """

	file_size: int
	""" One oversized write dies with SIGXFSZ instead of filling the shared tmpfs. """

	open_files: int = 256
	""" Enough for beet's own file handling, far short of exhausting the container. """

	def apply(self) -> None:
		""" Set every limit on the calling process, and start a new session.

		The new session matters as much as the limits: it gives the child its own process group, so a
		timeout can kill everything it spawned rather than only the process that was waited on.
		"""
		resource.setrlimit(resource.RLIMIT_AS, (self.address_space, self.address_space))
		resource.setrlimit(resource.RLIMIT_CPU, (self.cpu_seconds, self.cpu_seconds))
		resource.setrlimit(resource.RLIMIT_FSIZE, (self.file_size, self.file_size))
		resource.setrlimit(resource.RLIMIT_NOFILE, (self.open_files, self.open_files))
		resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
		os.setsid()


PLAYGROUND_RLIMITS: Rlimits = Rlimits(address_space=512 * 1024 * 1024, cpu_seconds=10, file_size=16 * 1024 * 1024)
""" Roughly 7x the 68.5 MB and 18x the 0.54 s a real playground project measures. """

HEADERS_RLIMITS: Rlimits = Rlimits(address_space=768 * 1024 * 1024, cpu_seconds=60, file_size=64 * 1024 * 1024)
""" Higher across the board: the work scales with the submitted pack rather than with fifteen lines.

The file size ceiling is what the output archive is written under, so it has to clear the 25 MB an
upload is allowed to be with room for the headers the job just added.
"""


class Job:
	""" One child process, from throwaway directory to parsed payload. """

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
			# A visitor clicking Run is not someone building a datapack.
			"STEWBEET_TELEMETRY": "0",
		}

	@staticmethod
	def reap() -> int:
		""" Reap orphaned descendants, so a fork bomb cannot exhaust the container's pid limit.

		The worker is PID 1 in the container, so anything a job left behind is reparented there and
		stays a zombie until someone waits on it. Zombies still occupy a pid, so a single fork bomb was
		enough to fill pids_limit and leave the worker unable to spawn a thread for the next
		connection, which the client saw as a dropped connection rather than an error.

		`init: true` in compose puts a real init in front of the worker and is the proper fix. This
		runs anyway, so the worker is not one deployment flag away from that failure.

		Safe against Popen's own bookkeeping because the caller has already waited on the child and
		only one job runs at a time, so nothing here is still tracked.

		Returns:
			int: How many processes were reaped.
		"""
		reaped: int = 0
		while True:
			try:
				pid, _ = os.waitpid(-1, os.WNOHANG)
			except ChildProcessError:
				return reaped
			if pid == 0:
				return reaped
			reaped += 1

	@staticmethod
	def sweep() -> None:
		""" Empty /tmp before a job starts.

		Pointing the child's TMPDIR at its own throwaway directory only redirects code that asks
		politely. Nothing stops submitted code from writing to /tmp directly, and those files outlive
		the request that made them, so without this the shared tmpfs would fill up one visitor at a
		time until every job failed on scratch space.

		Safe to do unconditionally because the caller holds the single job slot, so no other job owns
		anything under /tmp at this point.
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
	def workdir(prefix: str) -> str:
		""" Make a fresh throwaway directory with the cache folder the environment points at.

		Args:
			prefix (str): Name prefix, so a leaked directory says which job made it.
		Returns:
			str: Path of the new directory, which the caller must delete.
		"""
		created: str = tempfile.mkdtemp(dir="/tmp", prefix=prefix)
		os.makedirs(f"{created}/cache", exist_ok=True)
		return created

	@staticmethod
	def launch(argv: list[str], cwd: str, workdir: str, limits: Rlimits, wall_timeout: float) -> tuple[str, bool]:
		""" Run one runner under the given ceilings and return its stdout.

		The child is killed by process group, twice: once when the wait times out, and again in the
		finally, because a child that exited normally may still have left grandchildren behind.

		Args:
			argv         (list[str]): The runner and its arguments, after the interpreter.
			cwd          (str):       Working directory for the child.
			workdir      (str):       The per request directory, used as the child's home and temp.
			limits       (Rlimits):   Ceilings to apply between fork and exec.
			wall_timeout (float):     Wall clock ceiling. RLIMIT_CPU fires first for a busy loop; this
				covers sleep.
		Returns:
			tuple[str, bool]: The child's combined output, and whether it timed out.
		"""
		process: subprocess.Popen[str] = subprocess.Popen(
			[f"{SRV}/.venv/bin/python", *argv],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			stdin=subprocess.DEVNULL,
			cwd=cwd,
			env=Job.environment(workdir),
			text=True,
			errors="replace",
			preexec_fn=limits.apply,
		)
		try:
			output, _ = process.communicate(timeout=wall_timeout)
			return output, False
		except subprocess.TimeoutExpired:
			Job.kill(process)
			try:
				output, _ = process.communicate(timeout=KILL_GRACE)
			except subprocess.TimeoutExpired:
				# Something that outlived the kill still holds the write end of the stdout pipe, so
				# EOF will never come. Drop the log rather than block this thread forever with the
				# single job slot in hand.
				output = ""
			return output, True
		finally:
			Job.kill(process)
			if process.stdout is not None:
				process.stdout.close()

	@staticmethod
	def kill(process: subprocess.Popen[str]) -> None:
		""" SIGKILL the child's whole process group, until there is nothing left in it.

		One signal is not enough against something that forks in a loop. killpg reaches every process
		in the group at the instant it is delivered, but a fork that lands a microsecond later produces
		a child that inherits the group and was never signalled. So this repeats until killpg reports
		the group as empty, which is the only way to know.

		Args:
			process (subprocess.Popen[str]): The child to kill.
		"""
		try:
			group: int = os.getpgid(process.pid)
		except (ProcessLookupError, PermissionError):
			return

		deadline: float = time.monotonic() + KILL_GRACE
		while True:
			try:
				os.killpg(group, signal.SIGKILL)
			except (ProcessLookupError, PermissionError):
				return
			if time.monotonic() > deadline:
				return
			time.sleep(KILL_INTERVAL)

	@staticmethod
	def parse(output: str, timed_out: bool) -> dict[str, Any]:
		""" Split the child's stdout into log and JSON payload.

		A missing sentinel means the child died before it could report, which is what an OOM kill, a
		SIGXFSZ or a SIGKILL look like from here.

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
	def warnings(logs: str) -> list[str]:
		""" The warning lines of a log, which is all a caller with no room for the whole thing wants.

		Args:
			logs (str): The log, already stripped of colour by parse.
		Returns:
			list[str]: Every line stouputils marked as a warning, in order.
		"""
		return [line.strip() for line in logs.splitlines() if line.lstrip().startswith(WARNING_PREFIX)]

