
# Imports
from pathlib import Path

import stouputils as stp
from beet import Atlas, Context, ResourcePack
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.item import Item
from .object import AutoModel, to_atlas


# Utility function to add textures to atlas
def add_to_atlas(textures: set[str] = set()) -> None:  # noqa: B006
	""" Add textures to the specified atlas.

	Args:
		textures	(set[str]):	The set of texture paths to add. Defaults to an empty set.
	"""
	if not textures:
		return

	# Get mcmeta and setup overlays if needed
	rp: ResourcePack = Mem.ctx.assets

	# Define overlay configurations
	overlay_configs: list[JsonDict] = [
		{
			"directory": "before_format_73",
			"formats": [0, 72],
			"min_format": 0,
			"max_format": 72,
			"atlas_name": "blocks"
		},
		{
			"directory": "format_73_plus",
			"formats": [73, 1000],
			"min_format": 73,
			"max_format": 1000,
			"atlas_name": "items"
		}
	]

	# Process each overlay configuration
	for config in overlay_configs:
		directory: str = config["directory"]

		# Check if this overlay already exists
		rp.overlays[directory] = ResourcePack(
			name=directory,
			supported_formats=config["formats"],
			min_format=config["min_format"],
			max_format=config["max_format"]
		)

		# Add textures to the appropriate atlas in the overlay
		overlay = Mem.ctx.assets.overlays[directory]
		atlas_object: Atlas = overlay["minecraft"].atlases.setdefault(config["atlas_name"])
		data: JsonDict = atlas_object.data
		sources: list[JsonDict] = data.get("sources", [])

		for texture in textures:
			sources.append({"type": "minecraft:single", "resource": texture, "sprite": to_atlas(texture)})

		sources = stp.unique_list(sorted(sources, key=lambda x: x["resource"]))
		atlas_object.data["sources"] = sources
		atlas_object.encoder = stp.json_dump


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.resource_pack.item_models'")
def beet_default(ctx: Context):
	""" Main entry point for the item models plugin.

	Args:
		ctx (Context): The beet context.
	"""
	## Assertions
	# Stewbeet Initialized
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# Textures folder
	textures_folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert textures_folder != "", "Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. Please set a directory path in project configuration."

	# Textures
	textures: dict[str, str] = {
		stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
		for p in Path(textures_folder).rglob("*.png")
	}

	# Initialize rendered_item_models set in ctx.meta
	Mem.ctx.meta["stewbeet"]["rendered_item_models"] = set()

	# Get all item models from definitions
	item_models: dict[str, AutoModel] = {}
	for item_name in Mem.definitions.keys():
		obj = Item.from_id(item_name)

		# Skip items without models or already rendered
		item_model: str = obj.components.get("item_model", "")
		if not item_model or item_model in Mem.ctx.meta["stewbeet"]["rendered_item_models"]:
			continue

		# Skip items not in our namespace
		if not item_model.startswith(Mem.ctx.project_id):
			continue

		# Create an MyItemModel object from the definitions entry
		item_models[item_name] = AutoModel.from_definitions(obj, textures)

	# Process each item model
	used_minecraft_textures: set[str] = set()
	for model in item_models.values():
		used_minecraft_textures.update(model.process())

	# If any of the minecraft textures used are not in the items atlas, add them
	not_in_atlas: set[str] = {texture for texture in used_minecraft_textures if not texture.startswith("minecraft:item/")}
	add_to_atlas(textures=not_in_atlas)

