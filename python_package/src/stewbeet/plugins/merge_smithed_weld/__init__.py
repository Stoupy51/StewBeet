
# Imports
import os
from pathlib import Path

from beet import Context
from stouputils.decorators import measure_time
from stouputils.print import progress

from .weld import weld_datapack, weld_resource_pack


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.merge_smithed_weld'")
def beet_default(ctx: Context) -> None:
	""" Merge Smithed Weld plugin for StewBeet.
	Merges the generated datapack and resource pack with libraries using Smithed Weld.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	assert ctx.output_directory, "Output directory must be specified in the project configuration."
	assert ctx.project_name, "Project name must be specified in the project configuration."

	# Ensure output directory exists
	os.makedirs(ctx.output_directory, exist_ok=True)

	project_name_simple = ctx.project_name.replace(" ", "")

	# Generate destination paths for merged files
	datapack_dest = str(Path(ctx.output_directory) / f"{project_name_simple}_datapack_with_libs.zip")
	resource_pack_dest = str(Path(ctx.output_directory) / f"{project_name_simple}_resourcepack_with_libs.zip")

	# Call weld functions if the base archives exist
	datapack_source = str(Path(ctx.output_directory) / f"{project_name_simple}_datapack.zip")
	resource_pack_source = str(Path(ctx.output_directory) / f"{project_name_simple}_resourcepack.zip")

	if os.path.exists(datapack_source):
		weld_datapack(ctx, datapack_dest)

	if os.path.exists(resource_pack_source):
		weld_resource_pack(ctx, resource_pack_dest)

