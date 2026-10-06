
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Generator

import stouputils as stp
from beet import Context, Pipeline
from mecha import beet_default as mecha_plugin

from ...core.__memory__ import Mem
from .attribution import attribute_to as attribute_to, attributed as attributed
from .capture import install, record as record, tag as tag, uninstall
from .emit import write_maps as write_maps
from .mecha import write_maps as write_compiled_maps
from .origin import declaration_origin as declaration_origin, reset_caches, resolve_origin as resolve_origin

# Constants
PACKAGING_PLUGINS: tuple[str, ...] = (
	"stewbeet.plugins.archive",
	"stewbeet.plugins.merge_smithed_weld",
	"stewbeet.plugins.copy_to_destination",
	"stewbeet.plugins.compute_sha1",
)
""" StewBeet plugins that read the finished pack.
A map written after one of them ran is a map it did not see, which is the only reason to say anything about writing one late.
"""


# Main entry point
def beet_default(ctx: Context) -> Generator[None]:
	""" Record where every generated line came from, and map it once the build is done.

	Belongs in `require`, next to `stewbeet` itself, and that is the whole configuration.
	Everything there runs before the pack is even loaded, so no write can happen before capture is installed,
	and beet unwinds `require` last, so what mecha compiled is mapped from here too.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx
	Mem.sniffer_enabled = True
	# Reset here rather than in `plugins.initialize`, so a plain beet project requiring only this plugin works.
	# Every writer into this state is gated on `sniffer_enabled` or on a patch installed below, so it stays empty with the plugin off.
	Mem.source_map_chunks = {}
	Mem.source_map_origins = {}
	Mem.source_map_files = {}
	Mem.attribution = []
	reset_caches()
	install()

	yield

	try:
		# Without a `stewbeet.plugins.sniffer.emit` step or `stewbeet.plugins.archive`, nothing flushed the maps yet,
		# and writing them now keeps editor navigation working off the build directory.
		late: int = write_maps(ctx) if Mem.source_map_chunks else 0
		if late > 0:
			stp.info(f"sniffer: wrote {late} source map{'' if late == 1 else 's'} for what the helpers wrote")
		compiled: int = write_mecha_maps(ctx)

		if late > 0 and packaged(ctx):
			stp.warning(
				f"sniffer: those {late} source map(s) were written after the rest of the pipeline, so a plugin "
				"that packaged the pack did not see them. "
				"List 'stewbeet.plugins.sniffer.emit' before whichever plugin packages it."
			)
		elif not Mem.source_map_chunks and compiled == 0:
			stp.warning(
				"sniffer: nothing was captured, so no source maps were written. "
				"List 'stewbeet.plugins.sniffer' in 'require', next to 'stewbeet' itself."
			)
	finally:
		uninstall()
		Mem.sniffer_enabled = False


# Functions
def write_mecha_maps(ctx: Context) -> int:
	""" Map what mecha compiled, when mecha is part of the build.

	Done from here rather than from a pipeline entry of its own, because here is where it works:
	beet unwinds `require` last, so mecha has compiled, `auto.headers` has prepended its headers,
	and mecha's compilation units are still in its database. A bolt or mecha project with no StewBeet writes in it
	needs nothing more than this plugin either.

	Args:
		ctx: The beet context.
	Returns:
		How many sidecars this wrote.
	"""
	if mecha_plugin not in ctx.inject(Pipeline).plugins:
		return 0

	written: int = write_compiled_maps(ctx)
	if written > 0:
		stp.info(f"sniffer: wrote {written} source map{'' if written == 1 else 's'} for what mecha compiled")
	return written


def packaged(ctx: Context) -> bool:
	""" Whether a plugin that reads the finished pack ran in this build.

	Read off the plugins beet resolved rather than by importing each of them, since the question is only worth a name comparison.
	A packaging plugin of your own is not recognised, so nothing is said about a build that has one.

	Args:
		ctx: The beet context.
	"""
	return any(
		getattr(plugin, "__module__", "").startswith(PACKAGING_PLUGINS)
		for plugin in ctx.inject(Pipeline).plugins
	)

