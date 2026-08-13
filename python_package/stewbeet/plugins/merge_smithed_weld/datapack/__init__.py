
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context

from ..weld import weld_pack_types


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.merge_smithed_weld.datapack'")
def beet_default(ctx: Context) -> None:
	""" Merge only the datapack with its libraries, leaving the resource pack alone.

	Args:
		ctx (Context): The beet context.
	"""
	weld_pack_types(ctx, ("datapack",))
