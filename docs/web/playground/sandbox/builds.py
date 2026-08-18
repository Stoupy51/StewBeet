""" The two jobs the worker can run: a playground build, and an auto.headers pass over an upload.

Each one lays out a throwaway directory, hands it to its runner through jobs.Job, and deletes it
whatever happened in between. Neither keeps anything: the tmpfs is a shared budget and it is the only
writable place in the container, so a directory leaked here is taken away from every request that
follows.
"""
# Imports
import os
import shutil
import time
from typing import Any

from jobs import HEADERS_RLIMITS, PLAYGROUND_RLIMITS, SRV, Job

# Constants
WALL_TIMEOUT: float = 20.0
""" Wall clock ceiling for one playground build. RLIMIT_CPU fires first for a busy loop. """

HEADERS_WALL_TIMEOUT: float = 90.0
""" Wall clock ceiling for one headers pass, sized for a pack with thousands of functions. """


# Classes
class Build:
	""" One submitted playground build, from throwaway directory to parsed payload. """

	@staticmethod
	def link_assets(workdir: str) -> None:
		""" Give the build writable texture and render folders backed by the bundled ones.

		Both have to be writable, because src.placeholders adds a texture for every id the bundled
		packs do not cover and seeds a render for every definition, and the image is read only.
		Copying instead would spend a quarter of the tmpfs per request on bytes that are identical
		every time, so the build gets links: a few hundred inodes, no data, and the rglob("*.png") on
		the other side cannot tell the difference.

		Textures are linked file by file, since placeholders land beside them in the same folder.
		Renders are linked one namespace at a time, since a placeholder render goes into the project's
		own namespace, which no bundled pack provides.

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
		workdir: str = Job.workdir("build-")
		project: str = f"{workdir}/project"
		shutil.copytree(f"{SRV}/project", project)
		# beet.yml reads ../textures and ../iso_renders, so these sit beside the project.
		Build.link_assets(workdir)
		with open(f"{project}/src/user_code.py", "w", encoding="utf-8", newline="\n") as file:
			file.write(code)
		return workdir

	@staticmethod
	def run(code: str) -> dict[str, Any]:
		""" Prepare, build and clean up, whatever happens in between.

		Args:
			code (str): The submitted definitions module.
		Returns:
			dict[str, Any]: The payload, with the build duration added.
		"""
		started: float = time.monotonic()
		Job.sweep()
		workdir: str = Build.prepare(code)
		project: str = f"{workdir}/project"
		try:
			output, timed_out = Job.launch(
				[f"{SRV}/runner.py", project], cwd=project, workdir=workdir,
				limits=PLAYGROUND_RLIMITS, wall_timeout=WALL_TIMEOUT,
			)
			return Job.parse(output, timed_out) | {"durationMs": round((time.monotonic() - started) * 1000)}
		finally:
			shutil.rmtree(workdir, ignore_errors=True)
			# Both of the container's shared budgets, disk above and pids here, are given back before
			# the slot is released. Neither is allowed to be spent by a request that already finished.
			Job.reap()


class Headers:
	""" One uploaded datapack, run through stewbeet.plugins.auto.headers and handed straight back. """

	@staticmethod
	def prepare(pack: bytes) -> str:
		""" Lay out a fresh directory for one pass and drop the uploaded archive into it.

		Args:
			pack (bytes): The uploaded archive, already checked against the size ceiling.
		Returns:
			str: Path of the new directory, which the caller must delete.
		"""
		workdir: str = Job.workdir("headers-")
		with open(f"{workdir}/input.zip", "wb") as file:
			file.write(pack)
		return workdir

	@staticmethod
	def run(pack: bytes) -> tuple[dict[str, Any], bytes]:
		""" Rewrite the headers of the uploaded pack and return the new archive with it.

		The archive is read back into memory before the directory is deleted, because the point of
		this endpoint is that nothing outlives the request: the bytes go to the caller and the only
		copy left is the one in their browser.

		Args:
			pack (bytes): The uploaded archive.
		Returns:
			tuple[dict[str, Any], bytes]: The payload, and the rewritten archive, empty on failure.
		"""
		started: float = time.monotonic()
		Job.sweep()
		workdir: str = Headers.prepare(pack)
		try:
			output, timed_out = Job.launch(
				[f"{SRV}/headers_runner.py", workdir], cwd=workdir, workdir=workdir,
				limits=HEADERS_RLIMITS, wall_timeout=HEADERS_WALL_TIMEOUT,
			)
			payload: dict[str, Any] = Job.parse(output, timed_out)
			payload["durationMs"] = round((time.monotonic() - started) * 1000)
			if payload.get("ok") is not True:
				return payload, b""

			try:
				with open(f"{workdir}/output.zip", "rb") as file:
					archive: bytes = file.read()
			except OSError:
				# The runner said it succeeded and then the archive was not there, which only a kill
				# between the two can produce. Reported as a crash rather than as an empty download.
				return {"ok": False, "error": "crashed", "logs": payload.get("logs", "")}, b""
			return payload, archive
		finally:
			shutil.rmtree(workdir, ignore_errors=True)
			Job.reap()

