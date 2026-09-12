""" Emits `.mcfunction.map` sidecars for bolt and mecha, read straight off the compiled AST.

Same output contract as `stewbeet.plugins.sniffer`, an entirely different front half. Bolt's
positions were never lost, so there is no capture, no frame walk and no `difflib`: every
`mecha.AstNode` carries its own `location`, and column precision comes free.

Not to be confused with `mecha.contrib.source_map`, which prepends a header comment naming the file
and emits no line mapping at all.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from collections.abc import Iterator

import stouputils as stp
from beet import Context
from mecha import Mecha

from ....core.source_paths import origin_path, restore_filenames
from ..align import align
from ..model import SourceOrigin, WriteChunk
from ..sidecar import write_sidecar
from ..sources import reset_caches
from .attribute import candidate_sources, owner_of, source_file_of


# Functions
def project_roots(ctx: Context) -> tuple[str, ...]:
	""" Roots under which a compiled file counts as the project's own source.

	Defaults to beet's project directory. `meta.sniffer.roots` narrows it, which is what a project
	vendoring bolt libraries into its own tree needs: those compile into the pack and would
	otherwise be named as mapping targets.
	"""
	directory: str = os.path.abspath(str(ctx.directory))
	configured: list[str] = ctx.meta.get("sniffer", {}).get("roots", [])
	if configured:
		return tuple(os.path.normcase(os.path.abspath(os.path.join(directory, str(root)))) for root in configured)
	return (os.path.normcase(directory),)


def write_maps(ctx: Context) -> int:
	""" Write one sidecar per compiled function whose lines reach the project's own source.

	The serialised commands are reconciled against the function's final text rather than trusted
	positionally, because a StewBeet pipeline runs `auto.headers` after `mecha` and prepends a header
	block to every function. That is the same reason the StewBeet producer aligns, so it is the
	same `align`.

	Returns:
		How many sidecars were written.
	"""
	mc: Mecha = ctx.inject(Mecha)
	directory: str = os.path.abspath(str(ctx.directory))
	restore_filenames(mc, directory)
	sources: dict[str, str] = candidate_sources(mc, directory, project_roots(ctx))
	# A function mecha nested out of another one has no file of its own, and the text its AST was
	# parsed from is the parent file's own.
	parents: dict[str, str] = {text: path for path, text in sources.items()}

	# The database keys are the objects mecha compiled, which is the link a plain bolt project keeps
	# whatever else moves. A StewBeet build breaks it, because `auto.headers` replaces every function
	# object after mecha has compiled, so the resource location is what is left to match on.
	by_file = {file: unit for file, unit in mc.database.items() if unit.ast}
	by_location = {unit.resource_location: unit for unit in by_file.values() if unit.resource_location}

	written: int = 0
	for path, func in list(ctx.data.functions.items()):
		# A versioning refactor moves every function, and whether the unit is filed under the name
		# before or after the move is decided by whether mecha compiled before or after it.
		unit = by_file.get(func) or by_location.get(path) or by_location.get(origin_path(path))
		if unit is None or unit.ast is None:
			continue

		own_file: str | None = source_file_of(unit, directory) or parents.get(unit.source or "")

		chunks: list[WriteChunk] = []
		for command in unit.ast.commands:
			# A sentinel node carries no command and raises rather than serialising, which
			# `mecha.contrib.source_map` puts at the top of every function. Emitting no map is a
			# fair price for one; failing the build over a debug feature is not.
			try:
				serialized: str = mc.serialize(command)
			except Exception as error:
				stp.debug(f"sniffer.mecha: {path} has a node that does not serialise, skipping it ({error})")
				continue
			owner: str | None = owner_of(command.location, sources, serialized, unit.source, own_file)
			# mecha counts lines and columns from one, the map counts both from zero. A command is
			# one point in its source however many lines it serialises to, which is what exact=False says.
			origin: SourceOrigin | None = None if owner is None else SourceOrigin(
				file=owner, line=command.location.lineno - 1, column=command.location.colno - 1, exact=False,
			)
			chunks.append(WriteChunk(lines=tuple(serialized.split("\n")), origin=origin))

		if write_sidecar(ctx, path, func, align(chunks, func.text)):
			written += 1
	return written


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.sniffer.mecha'")
def beet_default(ctx: Context) -> Iterator[None]:
	""" Map every compiled function back to the module that wrote it.

	**For a project with no StewBeet writes in it.** `stewbeet.plugins.sniffer` calls `write_maps`
	itself from its own teardown, so a project listing that one needs nothing here, and listing both
	writes each sidecar once.

	**List this before `mecha` in the pipeline.** It does its work after the yield, and beet unwinds
	generator plugins in reverse, so listing it first is what leaves the `Module` compilation units
	and their sources in the database. Listed after `mecha`, they are already purged and every line
	comes out unmapped.

	Args:
		ctx (Context): The beet context.
	"""
	reset_caches()

	yield

	written: int = write_maps(ctx)
	stp.info(f"sniffer.mecha: wrote {written} source map{'' if written == 1 else 's'}")

