
# Imports
import stouputils as stp
from beet import Context

from .weld import ALL_PACK_TYPES, weld_pack_types


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.merge_smithed_weld'")
def beet_default(ctx: Context) -> None:
	""" Merge Smithed Weld plugin for StewBeet.
	Merges the generated datapack and resource pack with libraries using Smithed Weld.

	Welding a big pack costs seconds on every build, so prefer the split entry points
	``stewbeet.plugins.merge_smithed_weld.datapack`` and ``.resource_pack`` and list only the pack
	types the project actually ships. Listing both is equivalent to this one.

	Args:
		ctx (Context): The beet context.
	"""
	weld_pack_types(ctx, ALL_PACK_TYPES)
