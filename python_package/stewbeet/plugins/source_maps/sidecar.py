""" Turns resolved origins into a `.mcfunction.map` beside its function, for any producer.

Nothing here knows how the origins were found. The StewBeet path reconstructs them from write chunks and `difflib`;
the mecha path reads them off `AstNode.location`. Both hand the same `{generated line: origin}` mapping to `write_sidecar` and
get the same artifact.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from dataclasses import replace
from difflib import SequenceMatcher

import stouputils as stp
from beet import Context, Function, TextFile

from .encode import to_json
from .model import ColumnPoint, CompiledLine, FunctionSourceMap, LineMapping, SourceOrigin


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

	rendered: str | None = render_sidecar(path, func, mapped, pack_layout(ctx))
	if rendered is None:
		return False

	store_sidecar(ctx, path, rendered)
	return True


def render_sidecar(
	path: str, func: Function, mapped: dict[int, SourceOrigin], project_root: str
) -> str | None:
	""" The Source Map v3 JSON for one function, or None when none of its lines resolved.

	Split from `write_sidecar` so a producer holding a map it built earlier can put it in the pack
	without building it again.
	"""
	final: list[str] = final_lines_of(func.text)
	source_map: FunctionSourceMap | None = build_map(path, mapped, project_root, final)
	if source_map is None:
		return None
	return stp.json_dump(to_json(source_map, len(final)), max_level=2)


def store_sidecar(ctx: Context, path: str, rendered: str) -> None:
	""" Put a rendered map into the pack, beside the function it belongs to. """
	ctx.data.extra[f"{function_file_path(path)}.map"] = TextFile(rendered)


def has_sidecar(ctx: Context, path: str) -> bool:
	""" Whether the pack already carries this function's map.

	Asked before a producer resolves anything, since resolving origins is the expensive half and a
	sidecar is never written twice: `stewbeet.plugins.archive` flushes the maps, and the teardown of
	`stewbeet.plugins.source_maps` then walks the same functions again.
	"""
	return f"{function_file_path(path)}.map" in ctx.data.extra


def build_map(
	path: str, mapped: dict[int, SourceOrigin], project_root: str, final: list[str]
) -> FunctionSourceMap | None:
	""" Turn resolved origins into the artifact for one generated function.

	Args:
		final: Lines of the function's final text, which the columns of a compiled line are moved onto.
	"""
	if not mapped:
		return None

	sources: list[str] = []
	indices: dict[str, int] = {}
	rows: list[LineMapping] = []
	bolt: set[int] = set()
	opaque: set[tuple[int, int, int]] = set()
	for line in sorted(mapped):
		origin: SourceOrigin = mapped[line]
		if origin.file not in indices:
			indices[origin.file] = len(sources)
			sources.append(os.path.relpath(origin.file, project_root).replace(os.sep, "/"))

		index: int = indices[origin.file]
		compiled: CompiledLine | None = origin.compiled
		if compiled is not None and compiled.bolt:
			bolt.add(index)
		if compiled is not None and compiled.opaque is not None:
			opaque.add((index, *compiled.opaque))

		rows.append(LineMapping(
			generated_line=line,
			source_index=index,
			source_line=origin.line,
			source_column=origin.column,
			points=() if compiled is None or line >= len(final) else moved_points(compiled, final[line]),
		))

	file_path: str = function_file_path(path)
	return FunctionSourceMap(
		generated_path=path,
		sources=tuple(sources),
		mappings=tuple(rows),
		file=os.path.basename(file_path),
		bolt_sources=tuple(sorted(bolt)),
		opaque=tuple(sorted(opaque)),
	)


def moved_points(compiled: CompiledLine, final: str) -> tuple[ColumnPoint, ...]:
	""" The columns of a compiled line where they sit in the final text, which a later plugin may have edited.

	A versioning refactor turns `ns:impl/tick` into `ns:v1.2.3/tick` after mecha compiled it, see `moved_column`.
	A column inside text the edit replaced has no counterpart and is dropped.

	>>> points = (ColumnPoint(9, 0, 9), ColumnPoint(21, 0, 16))
	>>> compiled = CompiledLine("function ns:impl/tick", points, opaque=None, bolt=False)
	>>> [point.generated for point in moved_points(compiled, "function ns:v1.2.3/tick")]
	[9, 23]
	"""
	moved: list[ColumnPoint] = []
	for point in compiled.points:
		column: int | None = moved_column(point.generated, compiled.written, final)
		if column is not None:
			moved.append(replace(point, generated=column))
	return tuple(moved)


def moved_column(column: int, before: str, after: str) -> int | None:
	""" Where a column of a line sits in an edited copy of it, None when it falls in text the edit replaced.

	A versioning refactor turns `ns:impl/tick` into `ns:v1.2.3/tick`, before mecha parses or after it compiles,
	so a column is moved through the characters both lines share.

	>>> moved_column(21, "function ns:impl/tick", "function ns:v1.2.3/tick")
	23
	>>> moved_column(14, "function ns:impl/tick", "function ns:v1.2.3/tick") is None
	True
	"""
	if before == after:
		return column
	blocks = SequenceMatcher(None, before, after, autojunk=False).get_matching_blocks()
	return next((to + column - at for at, to, size in blocks if at <= column <= at + size), None)


def function_file_path(path: str) -> str:
	""" Pack-relative path of a generated function, from its resource location.

	>>> function_file_path("ns:foo/bar")
	'data/ns/function/foo/bar.mcfunction'
	"""
	namespace, _, name = path.partition(":")
	return f"data/{namespace}/function/{name}.mcfunction"


def pack_layout(ctx: Context) -> str:
	""" The project root every source is named relative to. """
	return os.path.abspath(str(ctx.directory))


def final_lines_of(text: str) -> list[str]:
	""" Lines of a function's final text, without the empty element a trailing newline leaves.

	>>> final_lines_of("say a\\nsay b\\n")
	['say a', 'say b']
	"""
	lines: list[str] = text.split("\n")
	return lines[:-1] if lines and lines[-1] == "" else lines

