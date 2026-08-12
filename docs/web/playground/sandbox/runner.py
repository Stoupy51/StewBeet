""" Build one submitted project and print the result, as the child process of worker.py.

This runs with the visitor's code already written to src/user_code.py, inside a throwaway copy of
the project, under the rlimits worker.py set before exec. It trusts none of that: the caps below
are re-applied here because a build that legitimately produces 40 000 files would otherwise be
serialized in full before anyone noticed.

Everything beet and stouputils print goes to stdout, so the payload is written after a sentinel
line and the parent keeps only what follows it.
"""
# Imports
import base64
import io
import json
import os
import sys
import traceback
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from typing import Any
from zipfile import ZipFile

# Constants
SENTINEL: str = "===STEWBEET-RESULT==="
""" Line after which stdout is the JSON payload and nothing else. """

MAX_FILES: int = 500
""" A two item project already emits 109 files, so this is roughly a fifteen item project. """

MAX_TOTAL_BYTES: int = 4 * 1024 * 1024
""" Total serialized output. The hero project measures 261 KB. """

MAX_FILE_BYTES: int = 256 * 1024
""" Per file, so one enormous texture cannot spend the whole budget on its own. """

BLOCKED_MODULES: tuple[str, ...] = (
	"model_resolver.render",
	"OpenGL",
	"glcontext",
	"moderngl",
)
""" Importing any of these means something in the pipeline wants a GPU.

Nothing in the configured pipeline reaches them: generate_all_iso_renders is only called by
ingame_manual, which is not in it. Blocking them turns a future pipeline change from a fifteen
second hang behind an OpenGL context into an immediate, readable error.
"""


# Classes
class BlockedImportFinder(MetaPathFinder):
	""" Meta path finder that refuses the modules above instead of letting them load. """

	def find_spec(self, fullname: str, path: Any = None, target: Any = None) -> ModuleSpec | None:
		""" Raise for a blocked module, and defer to the rest of sys.meta_path otherwise.

		Args:
			fullname (str): Fully qualified name of the module being imported.
			path     (Any): Unused, part of the MetaPathFinder protocol.
			target   (Any): Unused, part of the MetaPathFinder protocol.
		Returns:
			ModuleSpec | None: Always None, so the next finder on sys.meta_path decides.
		"""
		for blocked in BLOCKED_MODULES:
			if fullname == blocked or fullname.startswith(f"{blocked}."):
				raise ImportError(
					f"'{fullname}' is blocked in the playground: it needs an OpenGL context, which this "
					f"sandbox has no display for. Item renders and the in-game manual only run locally."
				)
		return None


# Functions
def dump_pack(pack: Any, prefix: str) -> dict[str, bytes]:
	""" Serialize a pack to the exact paths and bytes it would have written to disk.

	Going through a ZipFile in memory rather than an `output` directory keeps the build side effect
	free and still goes through beet's own dump path, so what the visitor sees is what they would
	get locally. Same helper as python_package/scripts/build_hero_output.py.

	Args:
		pack   (Any): The beet pack to serialize (`ctx.data` or `ctx.assets`).
		prefix (str): Folder the pack would have been written to, ex: "datapack".
	Returns:
		dict[str, bytes]: Mapping of build-relative path to file content.
	"""
	buffer: io.BytesIO = io.BytesIO()
	with ZipFile(buffer, "w") as archive:
		pack.dump(archive)
	with ZipFile(buffer) as archive:
		return {f"{prefix}/{name}": archive.read(name) for name in archive.namelist()}


def build(project: str) -> dict[str, bytes]:
	""" Run the project and return every file it generated.

	`cache=True` looks like a detail but is load bearing: with the default `cache=False` beet runs
	the whole build inside a temporary directory, and the project's relative paths then resolve
	against the wrong place. The cache lands in the throwaway copy and dies with it.

	Args:
		project (str): Directory holding beet.yml and src/.
	Returns:
		dict[str, bytes]: Mapping of build-relative path to file content.
	"""
	os.chdir(project)
	sys.path.insert(0, project)

	from beet import run_beet

	with run_beet(config=f"{project}/beet.yml", directory=project, cache=True) as ctx:
		return dump_pack(ctx.data, "datapack") | dump_pack(ctx.assets, "resource_pack")


def to_payload(built: dict[str, bytes]) -> dict[str, Any]:
	""" Split the build into a listing, decoded text and base64 images, within the caps.

	Text is normalized to LF because a lone CR is its own line break inside a <pre>, which shows up
	as double spaced output in the browser.

	Args:
		built (dict[str, bytes]): Mapping of build-relative path to file content.
	Returns:
		dict[str, Any]: Payload with `files`, `text`, `images` and `truncated`.
	"""
	files: list[dict[str, Any]] = []
	text: dict[str, str] = {}
	images: dict[str, str] = {}
	total: int = 0
	over_files: bool = False
	over_bytes: bool = False

	for path in sorted(built):
		if len(files) >= MAX_FILES:
			over_files = True
			break

		content: bytes = built[path]
		entry: dict[str, Any] = {"path": path, "bytes": len(content)}

		if len(content) > MAX_FILE_BYTES or total + len(content) > MAX_TOTAL_BYTES:
			over_bytes = True
			entry["kind"] = "skipped"
			files.append(entry)
			continue

		total += len(content)
		try:
			decoded: str = content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
			entry["kind"] = "text"
			entry["lines"] = decoded.count("\n") + 1
			text[path] = decoded
		except UnicodeDecodeError:
			entry["kind"] = "image"
			images[path] = base64.b64encode(content).decode("ascii")
		files.append(entry)

	return {
		"files": files,
		"text": text,
		"images": images,
		"truncated": {"files": over_files, "bytes": over_bytes},
	}


def main() -> int:
	""" Build the project named on the command line and print the payload after the sentinel.

	Returns:
		int: 0 when a payload was printed, whether the build succeeded or not.
	"""
	sys.meta_path.insert(0, BlockedImportFinder())

	if len(sys.argv) != 2:
		print(SENTINEL)
		print(json.dumps({"ok": False, "error": "usage: runner.py <project directory>"}))
		return 2

	try:
		payload: dict[str, Any] = {"ok": True} | to_payload(build(sys.argv[1]))
	except BaseException:
		payload = {"ok": False, "error": "build_failed", "traceback": traceback.format_exc()}

	print(SENTINEL)
	print(json.dumps(payload))
	return 0


if __name__ == "__main__":
	sys.exit(main())
