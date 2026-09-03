""" Writes the `.mcfunction.map` sidecars, as a pipeline step of its own.

It is separate from the capture plugin because the two have opposite ordering needs: capture must be
installed before anything writes a function, while emission must happen after every rewriting plugin
and still before `stewbeet.plugins.archive` zips the pack. A generator's teardown cannot sit between
those two, so the pipeline lists both.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os

import stouputils as stp
from beet import Context, TextFile

from ...core.__memory__ import Mem
from .align import align, final_lines_of
from .encode import to_json
from .model import FunctionSourceMap, LineMapping, SourceOrigin

# Constants
SOURCE_MAPPING_URL: str = "## sourceMappingURL="
""" Discovery comment appended as a function's last line. Two hashes, matching the reference implementation. """


# Functions
def function_file_path(path: str) -> str:
	""" Pack-relative path of a generated function, from its resource location.

	>>> function_file_path("ns:foo/bar")
	'data/ns/function/foo/bar.mcfunction'
	"""
	namespace, _, name = path.partition(":")
	return f"data/{namespace}/function/{name}.mcfunction"


def source_root_for(file_path: str, output_depth: int) -> str:
	""" Relative path from a map file's own directory back to the project root.

	Two things contribute: how deep the function sits inside the pack, and how deep the pack itself
	sits under the project root once it is dumped. Missing the second half lands on the pack root
	instead of the project root, and every `sources` entry then fails to resolve.

	Args:
		output_depth: Segments between the project root and the pack root, ex: 2 for build/datapack.

	>>> source_root_for("data/ns/function/foo.mcfunction", 2)
	'../../../../..'
	>>> source_root_for("data/ns/function/nested/foo.mcfunction", 2)
	'../../../../../..'
	"""
	directory_depth: int = len(file_path.split("/")) - 1
	return "/".join([".."] * (directory_depth + output_depth))


def pack_output_depth(ctx: Context) -> int:
	""" How many directories separate the project root from the dumped pack root. """
	project_root: str = os.path.abspath(str(ctx.directory))
	output: str = os.path.abspath(str(ctx.output_directory or project_root))
	relative: str = os.path.relpath(output, project_root)
	segments: list[str] = [part for part in relative.split(os.sep) if part not in (".", "")]
	return len(segments) + 1 # the pack writes into its own directory, named after the pack


def build_map(path: str, mapped: dict[int, SourceOrigin], project_root: str, output_depth: int) -> FunctionSourceMap | None:
	""" Turn resolved origins into the artifact for one generated function. """
	if not mapped:
		return None

	sources: list[str] = []
	indices: dict[str, int] = {}
	rows: list[LineMapping] = []
	for line in sorted(mapped):
		origin: SourceOrigin = mapped[line]
		if origin.file not in indices:
			indices[origin.file] = len(sources)
			sources.append(os.path.relpath(origin.file, project_root).replace(os.sep, "/"))
		rows.append(LineMapping(
			generated_line=line,
			source_index=indices[origin.file],
			source_line=origin.line,
			source_column=origin.column,
		))

	file_path: str = function_file_path(path)
	return FunctionSourceMap(
		generated_path=path,
		source_root=source_root_for(file_path, output_depth),
		sources=tuple(sources),
		mappings=tuple(rows),
		file=os.path.basename(file_path),
	)


def carries_discovery_comment(text: str) -> bool:
	""" Whether a function already ends with its `sourceMappingURL` line.

	Makes emission idempotent, so listing the step twice, or falling back to it at teardown after it
	already ran, never appends a second comment.

	>>> carries_discovery_comment("say hi\\n## sourceMappingURL=a.mcfunction.map\\n")
	True
	>>> carries_discovery_comment("say hi\\n")
	False
	"""
	return text.rstrip("\n").rsplit("\n", 1)[-1].startswith(SOURCE_MAPPING_URL)


def write_maps(ctx: Context) -> int:
	""" Write one `.mcfunction.map` beside every generated function that has a known origin.

	The discovery comment is appended **last** and is left unmapped on purpose: Sniffer counts
	comments and blank lines when placing breakpoints, so a leading comment would shift every
	mapped line by one.

	Returns:
		How many sidecars this call wrote, ignoring functions already carrying a comment.
	"""
	project_root: str = os.path.abspath(str(ctx.directory))
	output_depth: int = pack_output_depth(ctx)
	written: int = 0

	for path, func in list(ctx.data.functions.items()):
		chunks = Mem.source_map_chunks.get(path)
		if not chunks or carries_discovery_comment(func.text):
			continue

		source_map: FunctionSourceMap | None = build_map(path, align(chunks, func.text), project_root, output_depth)
		if source_map is None:
			continue

		# Append without collapsing trailing blank lines: those lines are mapped content, and
		# swallowing them would drop the comment onto an index that already carries an origin.
		file_path: str = function_file_path(path)
		body: str = func.text if func.text.endswith("\n") else f"{func.text}\n"
		func.text = f"{body}{SOURCE_MAPPING_URL}{source_map.file}.map\n"
		ctx.data.extra[f"{file_path}.map"] = TextFile(stp.json_dump(to_json(source_map, len(final_lines_of(func.text))), max_level=2))
		written += 1

	return written


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.sniffer.emit'")
def beet_default(ctx: Context) -> None:
	""" Write the source maps into the pack, before any plugin turns the pack into a distributable.

	Place it after every plugin that writes or rewrites functions, and before
	`stewbeet.plugins.archive`.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx
	count: int = write_maps(ctx)
	stp.info(f"sniffer: wrote {count} source map{'' if count == 1 else 's'}")

