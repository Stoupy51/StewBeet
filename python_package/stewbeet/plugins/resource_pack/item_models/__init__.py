""" 🎨 Generates the item models of the resource pack. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from pathlib import Path

import stouputils as stp
from beet import Atlas, Context, FormatSpecifier, ResourcePack
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.items.item import Item
from ....core.utils.io import setup_model_cache
from .object import AutoModel, to_atlas


# Major number of a pack format, which is an int or a [major, minor] pair
def major_of(pack_format: FormatSpecifier | None, default: int) -> int:
	if pack_format is None:
		return default
	return pack_format if isinstance(pack_format, int) else pack_format[0]


# Utility function to add textures to atlas
def add_to_atlas(textures: set[str] = set()) -> None:  # noqa: B006
	""" Add textures to the specified atlas.

	Args:
		textures: The set of texture paths to add. Defaults to an empty set.
	"""
	if not textures:
		return

	# The pack's own formats decide which configurations apply: none outside them, and one covering them all goes straight in the pack
	rp: ResourcePack = Mem.ctx.assets
	pack_first: int = major_of(rp.min_format, default=0)
	pack_last: int = major_of(rp.max_format, default=1000)
	overlay_configs: list[JsonDict] = [
		{"directory": "before_format_73", "min_format": 0, "max_format": 72, "atlas_name": "blocks"},
		{"directory": "format_73_plus", "min_format": 73, "max_format": pack_last, "atlas_name": "items"},
	]

	for config in overlay_configs:
		if config["max_format"] < pack_first or config["min_format"] > pack_last:
			continue
		directory: str = config["directory"]
		covers_pack: bool = config["min_format"] <= pack_first and config["max_format"] >= pack_last

		# Add textures to the appropriate atlas
		if not covers_pack:
			rp.overlays[directory] = ResourcePack(name=directory, min_format=config["min_format"], max_format=config["max_format"])
		target: ResourcePack = rp if covers_pack else rp.overlays[directory]
		atlas_object: Atlas = target["minecraft"].atlases.setdefault(config["atlas_name"])
		data: JsonDict = atlas_object.data
		sources: list[JsonDict] = data.get("sources", [])

		sources.extend({"type": "minecraft:single", "resource": texture, "sprite": to_atlas(texture)} for texture in textures)

		sources = stp.unique_list(sorted(sources, key=lambda x: x["resource"]))
		atlas_object.data["sources"] = sources
		atlas_object.encoder = stp.json_dump


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.resource_pack.item_models'")
def beet_default(ctx: Context):
	""" Main entry point for the item models plugin.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx

	# Serialized models are cached between builds by a hash of their content, see ModelSerializationCache.
	# They are encoded lazily at dump time, well after this plugin runs, so the cache only needs installing here.
	setup_model_cache(ctx)

	# Textures folder
	textures_folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert textures_folder != "", (
		"Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. "
		"Please set a directory path in project configuration."
	)

	# Textures
	textures: dict[str, str] = {
		stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
		for p in sorted(Path(textures_folder).rglob("*.png"), key=str)
	}

	# Initialize rendered_item_models set in ctx.meta
	Mem.ctx.meta["stewbeet"]["rendered_item_models"] = set()

	# Get all item models from definitions
	item_models: dict[str, AutoModel] = {}
	for item_name in Mem.definitions:
		obj = Item.from_id(item_name)

		# Skip items without models or already rendered
		item_model: str = obj.components.get("item_model", "")
		if not item_model or item_model in Mem.ctx.meta["stewbeet"]["rendered_item_models"]:
			continue

		# Skip items not in our namespace
		if obj.item_model.namespace != Mem.ctx.project_id:
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

