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
from beet import Context

from ...core.__memory__ import Mem
from .align import align
from .sidecar import write_sidecar


# Functions
def write_maps(ctx: Context) -> int:
	""" Write one `.mcfunction.map` beside every generated function that has a known origin.

	Returns:
		How many sidecars this call wrote, ignoring functions already carrying a comment.
	"""
	written: int = 0
	for path, func in list(ctx.data.functions.items()):
		chunks = Mem.source_map_chunks.get(path)
		if chunks and write_sidecar(ctx, path, func, align(chunks, func.text)):
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

