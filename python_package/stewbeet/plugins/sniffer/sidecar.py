""" Turns resolved origins into a `.mcfunction.map` beside its function, for any producer.

Nothing here knows how the origins were found. The StewBeet path reconstructs them from write
chunks and `difflib`; the mecha path reads them off `AstNode.location`. Both hand the same
`{generated line: origin}` mapping to `write_sidecar` and get the same artifact.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os

import stouputils as stp
from beet import Context, Function, TextFile

from .encode import to_json
from .model import FunctionSourceMap, LineMapping, SourceOrigin


# Functions
def write_sidecar(ctx: Context, path: str, func: Function, mapped: dict[int, SourceOrigin]) -> bool:
	""" Write one `.mcfunction.map` beside a generated function.

	Args:
		path:   Resource location of the function, ex: `mynamespace:v1.0/tick`.
		mapped: Origin per 0-based generated line. Lines with no origin are simply absent.
	Returns:
		False when there was nothing to map or the sidecar was already written.
	"""
	if not mapped or has_sidecar(ctx, path):
		return False

	project_root, output_depth = pack_layout(ctx)
	rendered: str | None = render_sidecar(path, func, mapped, project_root, output_depth)
	if rendered is None:
		return False

	store_sidecar(ctx, path, rendered)
	return True


def render_sidecar(
	path: str, func: Function, mapped: dict[int, SourceOrigin], project_root: str, output_depth: int
) -> str | None:
	""" The Source Map v3 JSON for one function, or None when none of its lines resolved.

	Split from `write_sidecar` so a producer holding a map it built earlier can put it in the pack
	without building it again.
	"""
	source_map: FunctionSourceMap | None = build_map(path, mapped, project_root, output_depth)
	if source_map is None:
		return None
	return stp.json_dump(to_json(source_map, len(final_lines_of(func.text))), max_level=2)


def store_sidecar(ctx: Context, path: str, rendered: str) -> None:
	""" Put a rendered map into the pack, beside the function it belongs to. """
	ctx.data.extra[f"{function_file_path(path)}.map"] = TextFile(rendered)


def has_sidecar(ctx: Context, path: str) -> bool:
	""" Whether the pack already carries this function's map.

	Asked before a producer resolves anything, since resolving origins is the expensive half and a
	sidecar is never written twice: `stewbeet.plugins.archive` flushes the maps, and the teardown of
	`stewbeet.plugins.sniffer` then walks the same functions again.
	"""
	return f"{function_file_path(path)}.map" in ctx.data.extra


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


def pack_layout(ctx: Context) -> tuple[str, int]:
	""" The project root every source is named relative to, and how deep the pack sits under it. """
	return os.path.abspath(str(ctx.directory)), pack_output_depth(ctx)


def pack_output_depth(ctx: Context) -> int:
	""" How many directories separate the project root from the dumped pack root. """
	project_root: str = os.path.abspath(str(ctx.directory))
	output: str = os.path.abspath(str(ctx.output_directory or project_root))
	relative: str = os.path.relpath(output, project_root)
	segments: list[str] = [part for part in relative.split(os.sep) if part not in (".", "")]
	return len(segments) + 1 # the pack writes into its own directory, named after the pack


def final_lines_of(text: str) -> list[str]:
	""" Lines of a function's final text, without the empty element a trailing newline leaves.

	>>> final_lines_of("say a\\nsay b\\n")
	['say a', 'say b']
	"""
	lines: list[str] = text.split("\n")
	return lines[:-1] if lines and lines[-1] == "" else lines

