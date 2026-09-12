""" Writes the `.mcfunction.map` sidecars for StewBeet's own writes, as a pipeline step of its own.

It is separate from the capture plugin because the two have opposite ordering needs: capture must be
installed before anything writes a function, while emission must happen after every rewriting plugin
and still before `stewbeet.plugins.archive` zips the pack. A generator's teardown cannot sit between
those two, so the pipeline lists both.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Cache, Context, Function

from ....core.__memory__ import Mem
from ....core.source_paths import origin_path
from ..align import align
from ..cache import CACHE_NAME, load_maps, map_signature, store_maps
from ..model import WriteChunk
from ..sidecar import has_sidecar, pack_layout, render_sidecar, store_sidecar


# Functions
def write_maps(ctx: Context) -> int:
	""" Write one `.mcfunction.map` beside every generated function that has a known origin.

	A function whose chunks, text and pack layout are all unchanged since the last build gets its map
	back from the cache instead of being reconciled again, which is where nearly all of the time goes.

	Returns:
		How many sidecars this call wrote, ignoring functions already carrying a comment.
	"""
	# Chunks are filed under the path the write named, which a versioning refactor then moves.
	pending: list[tuple[str, Function, list[WriteChunk]]] = [
		(path, func, chunks)
		for path, func in list(ctx.data.functions.items())
		if not has_sidecar(ctx, path)
		and (chunks := Mem.source_map_chunks.get(path) or Mem.source_map_chunks.get(origin_path(path)))
	]
	if not pending:
		return 0

	project_root, output_depth = pack_layout(ctx)
	layout: str = f"{project_root}\0{output_depth}"
	cache: Cache = ctx.cache[CACHE_NAME]
	remembered: dict[str, tuple[str, str]] = load_maps(cache)
	# An earlier flush in this same build already stored what it wrote, and those functions are
	# skipped above, so their entries are carried over rather than dropped from the record.
	fresh: dict[str, tuple[str, str]] = {
		path: entry for path, entry in remembered.items() if path in ctx.data.functions
	}

	written: int = 0
	for path, func, chunks in pending:
		signature: str = map_signature(chunks, func.text, layout)
		previous: tuple[str, str] | None = remembered.get(path)

		rendered: str | None
		if previous is not None and previous[0] == signature:
			rendered = previous[1]
		else:
			rendered = render_sidecar(path, func, align(chunks, func.text), project_root, output_depth)
		if rendered is None:
			fresh.pop(path, None)
			continue

		store_sidecar(ctx, path, rendered)
		fresh[path] = (signature, rendered)
		written += 1

	store_maps(cache, fresh)
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

