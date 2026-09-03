
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Iterator

import stouputils as stp
from beet import Context

from ...core.__memory__ import Mem
from .attribution import attribute_to as attribute_to
from .capture import install, record as record, tag as tag, uninstall
from .emit import write_maps as write_maps
from .origin import reset_caches, resolve_origin as resolve_origin


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.sniffer'")
def beet_default(ctx: Context) -> Iterator[None]:
	""" Record where every generated line came from, so `stewbeet.plugins.sniffer.emit` can map it.

	Belongs in `require`, next to `stewbeet` itself: everything there runs before the pack is even
	loaded, so no write can happen before capture is installed. A pipeline entry works too, as long
	as it sits before every plugin that writes a function.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx
	Mem.sniffer_enabled = True
	reset_caches()
	install()

	yield

	try:
		if not Mem.source_map_chunks:
			stp.warning(
				"sniffer: nothing was captured, so no source maps were written. "
				"List 'stewbeet.plugins.sniffer' in 'require', next to 'stewbeet' itself."
			)
		elif late := write_maps(ctx):
			# Reaching here means the emit step never ran. Writing the maps anyway keeps editor
			# navigation working off the build directory, but anything already packaged missed them.
			stp.warning(
				f"sniffer: {late} source map(s) were written after the rest of the pipeline, so plugins "
				"like 'stewbeet.plugins.archive' did not see them. "
				"List 'stewbeet.plugins.sniffer.emit' just before 'stewbeet.plugins.archive'."
			)
	finally:
		uninstall()
		Mem.sniffer_enabled = False

