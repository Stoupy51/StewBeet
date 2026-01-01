
# Imports
import os
import shutil
from typing import cast

import requests
import stouputils as stp
from beet import Model
from beet.core.utils import JsonDict
from model_resolver.render import Render

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from ...core.constants import (
	DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE,
	DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW,
)
from .shared_import import SharedMemory


# Generate iso renders for every item in the definitions
def generate_all_iso_renders():
	ns: str = Mem.ctx.project_id

	# Create the items folder
	path = SharedMemory.cache_path + "/items"
	os.makedirs(f"{path}/{ns}", exist_ok = True)

	# For every item, get the model path and the destination path
	cache_assets: bool = Mem.ctx.meta.get("stewbeet",{}).get("manual", {}).get("cache_assets", True)
	for_model_resolver: dict[str, str] = {}
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)

		# Skip items that don't have models
		if not obj.components.get("item_model"):
			continue

		# Skip if item is already generated (to prevent OpenGL launching for nothing)
		if os.path.exists(f"{path}/{ns}/{item}.png") and cache_assets:
			continue

		# Add to the model resolver queue (only if present in resource pack)
		model: Model | None = Mem.ctx.assets[ns].models.get(f"item/{item}")
		rp_path = f"{ns}:item/{item}"
		dst_path = f"{path}/{ns}/{item}.png"
		if model is not None and model.get_content().get("textures", None) is not None: # type: ignore
			for_model_resolver[rp_path] = dst_path

	# Launch model resolvers for remaining blocks
	if len(for_model_resolver) > 0:

		## Model Resolver v0.12.0
		# model_resolver_main(
		# 	render_size = config['opengl_resolution'],
		# 	load_dir = load_dir,
		# 	output_dir = None,	# type: ignore
		# 	use_cache = False,
		# 	minecraft_version = "latest",
		# 	__special_filter__ = for_model_resolver	# type: ignore
		# )

		# If atlas is used in overlay, copy it
		any_atlas_used: bool = "before_format_73" in Mem.ctx.assets.overlays._wrapped.keys() # type: ignore
		if any_atlas_used:
			Mem.ctx.assets["minecraft"].atlases["temporary_stewbeet"] = Mem.ctx.assets.overlays["before_format_73"]["minecraft"].atlases["blocks"]

		## Model Resolver >= v1.12.0
		stp.debug(f"Generating iso renders for {len(for_model_resolver)} items, this may take a while...")
		render = Render(Mem.ctx)
		for rp_path, dst_path in for_model_resolver.items():
			render.add_model_task(rp_path, path_save=dst_path, animation_mode="one_file")
		render.run()
		stp.debug("Generated iso renders for all items")

		# Remove temporary atlas
		if any_atlas_used:
			del Mem.ctx.assets["minecraft"].atlases["temporary_stewbeet"]

	## Copy every used vanilla items
	# Get every used vanilla items
	used_vanilla_items: set[str] = set()
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)
		for recipe in obj.recipes:
			ingredients = []
			if recipe.get("ingredients"):
				ingredients = recipe["ingredients"]
				if isinstance(ingredients, dict):
					ingredients = cast(list[JsonDict], ingredients.values())
			elif recipe.get("ingredient"):
				ingredients = [recipe["ingredient"]]
			for ingredient in ingredients:
				if "item" in ingredient:
					used_vanilla_items.add(ingredient["item"].split(":")[1])
			if recipe.get("result") and recipe["result"].get("item"):
				used_vanilla_items.add(recipe["result"]["item"].split(":")[1])
		pass

	# Download all the vanilla textures from the wiki
	def download_item(item: str, destination: str = ""):
		if not destination:
			destination = f"{path}/minecraft/{item}.png"
		if not (os.path.exists(destination) and cache_assets):	# If not downloaded yet or not using cache
			for base_link in (DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW, DOWNLOAD_VANILLA_ASSETS_RAW):
				for folder in ["item", "block", "items"]:
					link: str = f"{base_link}/{folder}/{item}.png"
					response = requests.get(link)
					if response.status_code == 200:
						with stp.super_open(destination, "wb") as file:
							return file.write(response.content)
			# If all attempts failed
			stp.warning(f"Failed to download texture for '{item}', please add it manually to '{destination}'")
			stp.warning(f"Suggestion link: '{DOWNLOAD_VANILLA_ASSETS_SOURCE}'")

	# Multithread the download
	stp.multithreading(download_item, used_vanilla_items, max_workers=min(32, len(used_vanilla_items)))

	# Download painting texture for custom paintings
	last_painting_path: str = ""
	for item, data in Mem.definitions.items():
		if data["id"] == "minecraft:painting" and not data.get("item_model"):
			if not last_painting_path:
				last_painting_path = f"{path}/{ns}/{item}.png"
				download_item("painting", last_painting_path)
			else:
				# Just copy the last painting downloaded
				shutil.copy(last_painting_path, f"{path}/{ns}/{item}.png")

