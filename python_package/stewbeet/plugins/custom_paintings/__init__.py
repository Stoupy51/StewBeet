
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from pathlib import Path

import stouputils as stp
from beet import Atlas, Context, PaintingVariant, PaintingVariantTag, Texture
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.painting import Painting
from ...core.constants import PAINTING_DATA
from ...core.utils.io import set_json_encoder, texture_mcmeta


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.custom_paintings'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the custom paintings plugin.
	This plugin handles the generation of custom paintings for the datapack and resource pack.

	Requires a valid definitions in Mem.definitions in order to function properly using constant 'PAINTING_DATA'.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")
	placeable_values: list[str] = []
	paintings_sources: list[JsonDict] = []

	# Assertions
	assert textures_folder, "The 'textures_folder' key is missing in the 'stewbeet' section of the beet.yml file."

	# For each item definition that has painting data,
	for item, data in Mem.definitions.items():
		painting_data: JsonDict = data.get(PAINTING_DATA, {})
		if painting_data:
			obj_painting = Painting.from_id(item)

			## Datapack
			# Add the item id to the list of painting variants values
			if not painting_data.get("not_placeable", False):
				placeable_values.append(obj_painting.variant)

			# Set default author and title if not provided
			if "author" not in painting_data:
				painting_data["author"] = {"text": Mem.ctx.project_author or "Unknown"}
			if "title" not in painting_data:
				painting_data["title"] = data.get("item_name") or {"text": item.replace("_", " ").title()}

			# Create ordered painting data with asset_id first
			ordered_painting_data = {"asset_id": obj_painting.asset_id}
			ordered_painting_data.update(painting_data)
			ordered_painting_data.pop("not_placeable", None)
			ordered_painting_data.pop("texture", None)

			# Create the painting definition
			obj_painting.variant.write(set_json_encoder(PaintingVariant(ordered_painting_data)))

			## Resource pack
			# Get the texture path
			if "texture" in painting_data:
				texture: str = painting_data["texture"]
				src: str = stp.relative_path(f"{textures_folder}/{texture}.png")
			else:
				matching_textures: list[str] = sorted(
					stp.relative_path(f"{root}/{file}")
					for root, _, files in os.walk(textures_folder)
					for file in files if file == f"{item}.png"
				)
				if not matching_textures:
					stp.error(
						f"No texture found for painting '{item}' in the textures folder '{textures_folder}'. "
						f"Expected a file named '{item}.png'."
					)
					continue
				if len(matching_textures) > 1:
					stp.warning(
						f"Multiple textures found for painting '{item}' in the textures folder '{textures_folder}'. "
						f"Using the first one found: '{matching_textures[0]}'."
					)
				src: str = matching_textures[0]

			# Reuse the item texture through the paintings atlas rather than shipping the same image twice
			item_texture: Texture | None = obj_painting.texture.get()
			if item_texture and item_texture.source_path and Path(item_texture.source_path).resolve() == Path(src).resolve():
				paintings_sources.append(
					{"type": "minecraft:single", "resource": obj_painting.texture, "sprite": obj_painting.asset_id}
				)
			elif not obj_painting.painting_texture.exists():
				obj_painting.painting_texture.write(texture_mcmeta(src))

	if paintings_sources:
		Mem.ctx.assets["minecraft"].atlases["paintings"] = set_json_encoder(Atlas({"sources": paintings_sources}))

	# Add the painting variant tag to the context data
	if placeable_values:
		placeable_tag: PaintingVariantTag = PaintingVariantTag({"values": placeable_values})
		Mem.ctx.data["minecraft"].painting_variant_tags["placeable"] = set_json_encoder(placeable_tag)

