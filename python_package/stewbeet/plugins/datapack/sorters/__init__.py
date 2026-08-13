
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context
from stouputils.typing import JsonDict

from .constants import SorterFile
from .match import generate_sorter


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.datapack.sorters'")
def beet_default(ctx: Context):
	""" Main entry point for the sorters plugin.
	This plugin generates functions that sort lists in storage.

	Args:
		ctx (Context): The beet context.
	"""
	ctx.data.extend_namespace.append(SorterFile)

	# Iterate through all sorter configurations
	for file_instance in ctx.data[SorterFile].values():
		sorter: JsonDict = file_instance.data.model_dump()
		generate_sorter(ctx, sorter)

	# Clear the registry
	ctx.data[SorterFile].clear()

