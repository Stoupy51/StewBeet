
# Imports
from pathlib import Path

from beet import Context
from stouputils.decorators import measure_time
from stouputils.io import clean_path, relative_path
from stouputils.print import progress

from ....core.__memory__ import Mem
from .object import AutoModel


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.resource_pack.item_models'")
def beet_default(ctx: Context):
	""" Main entry point for the item models plugin.

	Args:
		ctx (Context): The beet context.
	"""
	## Assertions
	# Stewbeet Initialized
	if Mem.ctx is None:
		Mem.ctx = ctx
	# Textures folder
	textures_folder: str = relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert textures_folder != "", "Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. Please set a directory path in project configuration."

	# Textures
	textures: dict[str, str] = {
		clean_path(str(p)).split("/")[-1]: relative_path(p)
		for p in Path(textures_folder).rglob("*.png")
	}

	# Initialize rendered_item_models set in ctx.meta
	Mem.ctx.meta["stewbeet"]["rendered_item_models"] = set()

	# Get all item models from database
	item_models: dict[str, AutoModel] = {}
	for item_name, data in Mem.database.items():

		# Skip items without models or already rendered
		item_model: str = data.get("item_model", "")
		if not item_model or item_model in Mem.ctx.meta["stewbeet"]["rendered_item_models"]:
			continue

		# Skip items not in our namespace
		if not item_model.startswith(Mem.ctx.project_id):
			continue

		# Create an MyItemModel object from the database entry
		item_models[item_name] = AutoModel.from_database(item_name, data, textures)

	# Process each item model
	for model in item_models.values():
		model.process()

