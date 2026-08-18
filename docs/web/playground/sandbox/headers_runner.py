""" Rewrite the headers of an uploaded datapack, as the child process of worker.py.

This runs with the upload already written to `input.zip` inside a throwaway directory, under the
ceilings jobs.HEADERS_RLIMITS set before exec. It trusts none of that: the caps below are re-applied
here because a 25 MB archive of zeroes expands to far more than the tmpfs holds, and finding that out
halfway through is worse than refusing it up front.

The output is deliberately not beet's own dump. Only the `.mcfunction` files auto.headers touched are
written back over the extracted upload, which is then re-zipped as it stands. Dumping the pack
instead would re-encode every JSON file in it, and a tool whose job is to add comments to functions
has no business reformatting a loot table.

Everything beet and stouputils print goes to stdout, so the payload is written after a sentinel line
and the parent keeps only what follows it.
"""
# Imports
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from errors import root_cause

# Constants
SENTINEL: str = "===STEWBEET-RESULT==="
""" Line after which stdout is the JSON payload and nothing else. """

MAX_ENTRIES: int = 20_000
""" Entry count ceiling. A large real pack sits in the low thousands. """

MAX_EXTRACTED_BYTES: int = 192 * 1024 * 1024
""" Total uncompressed size, which is what a zip bomb runs into before the tmpfs does.

Sized against the upload ceiling rather than picked round: datapacks are text and text deflates by
roughly seven to one, so anything under this is reachable by a 25 MB archive that is not hostile.
"""

FUNCTION_SCOPES: tuple[str, ...] = ("function", "functions")
""" Both spellings beet accepts on input, so a pack written for either pack format is understood. """


# Functions
def extract(archive: Path, destination: Path) -> None:
	""" Unpack the upload, refusing anything that would escape the destination or fill the tmpfs.

	`ZipFile.extract` sanitizes paths on its own, but doing it here is what makes the rule visible and
	is also where the budgets are enforced. `..` and absolute paths are the escape; the running total
	is the bomb.

	Args:
		archive     (Path): The uploaded archive.
		destination (Path): Directory to unpack into, which must already exist.
	Raises:
		ValueError: When the archive is over one of the ceilings or tries to write outside.
	"""
	with ZipFile(archive) as zipped:
		entries = zipped.infolist()
		if len(entries) > MAX_ENTRIES:
			raise ValueError("too_many_entries")
		if sum(entry.file_size for entry in entries) > MAX_EXTRACTED_BYTES:
			raise ValueError("pack_too_large_extracted")

		root: Path = destination.resolve()
		for entry in entries:
			if entry.is_dir():
				continue
			parts = [part for part in entry.filename.replace("\\", "/").split("/") if part not in ("", ".")]
			if any(part == ".." for part in parts) or entry.filename.startswith("/"):
				raise ValueError("unsafe_archive")

			target: Path = root.joinpath(*parts)
			if not target.resolve().is_relative_to(root):
				raise ValueError("unsafe_archive")

			target.parent.mkdir(parents=True, exist_ok=True)
			with zipped.open(entry) as source, open(target, "wb") as file:
				file.write(source.read())


def find_root(extracted: Path) -> Path | None:
	""" The directory the datapack actually starts at.

	An upload is as often `MyPack.zip` holding `pack.mcmeta` at the top as it is a zip of the folder
	containing it, so both have to work. The shallowest `pack.mcmeta` wins, which is the outer pack
	when someone has bundled another one inside it.

	Args:
		extracted (Path): Where the archive was unpacked.
	Returns:
		Path | None: The pack root, or None when the upload holds no pack.mcmeta at all.
	"""
	found = sorted(extracted.rglob("pack.mcmeta"), key=lambda path: (len(path.parts), str(path)))
	return found[0].parent if found else None


def function_files(root: Path) -> dict[str, Path]:
	""" Map every function beet will report back to the file it was read from.

	Computing the output path from the pack format instead would mean trusting a pack.mcmeta a
	stranger wrote, and would silently move a function whose pack declares one format and is laid out
	for the other. The file that was read is the file that gets written.

	Args:
		root (Path): The pack root, holding pack.mcmeta and data/.
	Returns:
		dict[str, Path]: Absolute path of each function, keyed the way beet keys it, ex: "ns:foo/bar".
	"""
	files: dict[str, Path] = {}
	data: Path = root / "data"
	if not data.is_dir():
		return files

	for namespace in sorted(data.iterdir()):
		if not namespace.is_dir():
			continue
		for scope in FUNCTION_SCOPES:
			base: Path = namespace / scope
			if not base.is_dir():
				continue
			for path in base.rglob("*.mcfunction"):
				files[f"{namespace.name}:{path.relative_to(base).with_suffix('').as_posix()}"] = path
	return files


def rewrite(root: Path, workdir: Path) -> tuple[int, int]:
	""" Run auto.headers over the pack and write the functions it changed back to their own files.

	The pipeline is empty and the plugin is required from inside the build, rather than named in the
	config, because the pack is loaded from a path a stranger chose: a folder called `pack[1]` is a
	perfectly ordinary name and a glob pattern that matches nothing, and beet's `load` option goes
	through `glob`. Loading it directly has no such reading of the path.

	Args:
		root    (Path): The pack root.
		workdir (Path): The throwaway directory, which beet uses for its cache.
	Returns:
		tuple[int, int]: How many functions the pack has, and how many came back different.
	"""
	from beet import run_beet

	with run_beet(config={"id": "headers", "name": "headers"}, directory=workdir, cache=True) as ctx:
		ctx.data.load(root)
		ctx.require("stewbeet.plugins.auto.headers")
		rewritten: dict[str, str] = {path: function.text for path, function in ctx.data.functions.items()}

	files: dict[str, Path] = function_files(root)
	changed: int = 0
	for path, text in rewritten.items():
		target: Path | None = files.get(path)
		if target is None:
			continue
		content: bytes = text.encode("utf-8")
		# Beet normalizes every function to LF with a trailing newline, so an untouched pack would
		# still come back with every file rewritten. Comparing first keeps the archive as it was.
		if target.read_bytes() == content:
			continue
		target.write_bytes(content)
		changed += 1
	return len(files), changed


def repack(source: Path, archive: Path) -> None:
	""" Zip the extracted tree back up exactly as it stands.

	Args:
		source  (Path): Directory to zip, whose own name is not part of the entry paths.
		archive (Path): Archive to write.
	"""
	with ZipFile(archive, "w", ZIP_DEFLATED) as zipped:
		for path in sorted(source.rglob("*")):
			if path.is_file():
				zipped.write(path, path.relative_to(source).as_posix())


def main() -> int:
	""" Rewrite the pack in the directory named on the command line and print the payload.

	Returns:
		int: 0 when a payload was printed, whether the pass succeeded or not.
	"""
	if len(sys.argv) != 2:
		print(SENTINEL)
		print(json.dumps({"ok": False, "error": "usage: headers_runner.py <work directory>"}))
		return 2

	workdir: Path = Path(sys.argv[1])
	extracted: Path = workdir / "pack"
	payload: dict[str, Any]

	try:
		extracted.mkdir(parents=True, exist_ok=True)
		extract(workdir / "input.zip", extracted)

		root: Path | None = find_root(extracted)
		if root is None:
			payload = {"ok": False, "error": "no_pack_mcmeta"}
		else:
			os.chdir(workdir)
			functions, changed = rewrite(root, workdir)
			repack(extracted, workdir / "output.zip")
			payload = {"ok": True, "functions": functions, "changed": changed}
	except BadZipFile:
		payload = {"ok": False, "error": "invalid_archive"}
	except ValueError as error:
		payload = {"ok": False, "error": str(error)}
	except BaseException as error:
		cause: BaseException = root_cause(error)
		payload = {
			"ok": False,
			"error": "headers_failed",
			"message": f"{type(cause).__name__}: {cause}",
			"traceback": traceback.format_exc(),
		}

	print(SENTINEL)
	print(json.dumps(payload))
	return 0


if __name__ == "__main__":
	sys.exit(main())

