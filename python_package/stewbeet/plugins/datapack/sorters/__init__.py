
# Imports
from typing import Any

from beet import Context
from stouputils.decorators import measure_time
from stouputils.print import progress

from .constants import SorterFile
from .match import generate_sorter


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.datapack.sorters'")
def beet_default(ctx: Context):
	""" Main entry point for the sorters plugin.
	This plugin generates functions that sort lists in storage.

	Args:
		ctx (Context): The beet context.
	"""
	ctx.data.extend_namespace.append(SorterFile)

	# Iterate through all sorter configurations
	for file_instance in ctx.data[SorterFile].values():
		sorter: dict[str, Any] = file_instance.data.dict()
		generate_sorter(ctx, sorter)

	# Clear the registry
	ctx.data[SorterFile].clear()

