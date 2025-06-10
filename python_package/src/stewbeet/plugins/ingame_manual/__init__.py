
# Imports
from beet import Context
from beet.core.utils import JsonDict
from stouputils.decorators import measure_time
from stouputils.print import progress, warning

from ...core.__memory__ import Mem
from .main import main as manual_main
from .shared_import import SharedMemory


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.ingame_manual'")
def beet_default(ctx: Context):
	""" Main entry point for the ingame manual plugin.
	This plugin generates an in-game manual/guide book with item information and crafting recipes.

	Args:
		ctx (Context): The beet context.
	"""
	# Set up memory context
	if Mem.ctx is None:
		Mem.ctx = ctx

	# Only generate manual if we have definitions items
	if not Mem.definitions:
		warning("Database is empty, skipping manual generation.")
		return

	# Assertions
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	assert ctx.project_name, "Project name is not set. Please set it in the project configuration."
	assert ctx.project_author, "Project author is not set. Please set it in the project configuration."
	assert ctx.output_directory, "Output directory must be specified in the project configuration."
	stewbeet: JsonDict = ctx.meta.get("stewbeet", {})
	assert stewbeet, "stewbeet configuration is not set. Please set it in the project configuration."
	assert stewbeet.get("textures_folder"), "Textures folder is not set. Please set it in the project configuration."
	manual_config = stewbeet.get("manual", {})
	assert manual_config, "Manual configuration is not set. Please set it in the project configuration."

	# Set up manual path
	SharedMemory.cache_path = manual_config.get("cache_path", "")
	assert SharedMemory.cache_path, "Manual cache path is not set. Please set it in the project configuration."

	# Set up high resolution in the shared_import module
	SharedMemory.high_resolution = manual_config.get("high_resolution", True)

	# Call the main manual generation function
	manual_main()

