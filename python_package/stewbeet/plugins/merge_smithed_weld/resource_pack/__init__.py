
# Imports
import stouputils as stp
from beet import Context

from ..weld import weld_pack_types


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.merge_smithed_weld.resource_pack'")
def beet_default(ctx: Context) -> None:
	""" Merge only the resource pack with its libraries, leaving the datapack alone.

	Args:
		ctx (Context): The beet context.
	"""
	weld_pack_types(ctx, ("resource_pack",))
