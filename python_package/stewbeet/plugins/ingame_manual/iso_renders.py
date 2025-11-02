
# Imports
import os
import shutil
from typing import cast

import requests
from beet import Model
from beet.core.utils import JsonDict
from model_resolver.render import Render
from stouputils.io import super_open
from stouputils.parallel import multithreading
from stouputils.print import debug, warning

from ...core.__memory__ import Mem
from ...core.constants import (
	DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE,
	DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW,
	RESULT_OF_CRAFTING,
	USED_FOR_CRAFTING,
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
	for item, data in Mem.definitions.items():

		# Skip items that don't have models
		if not data.get("item_model"):
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

		## Model Resolver >= v1.8.2
		debug(f"Generating iso renders for {len(for_model_resolver)} items, this may take a while...")
		render = Render(Mem.ctx)
		for rp_path, dst_path in for_model_resolver.items():
			render.add_model_task(rp_path, path_save=dst_path, animation_mode="one_file")
		render.run()
		debug("Generated iso renders for all items")

	## Copy every used vanilla items
	# Get every used vanilla items
	used_vanilla_items: set[str] = set()
	for data in Mem.definitions.values():
		all_crafts: list[JsonDict] = list(data.get(RESULT_OF_CRAFTING,[]))
		all_crafts += list(data.get(USED_FOR_CRAFTING,[]))
		for recipe in all_crafts:
			ingredients = []
			if "ingredients" in recipe:
				ingredients = recipe["ingredients"]
				if isinstance(ingredients, dict):
					ingredients = cast(list[JsonDict], ingredients.values())
			elif "ingredient" in recipe:
				ingredients = [recipe["ingredient"]]
			for ingredient in ingredients:
				if "item" in ingredient:
					used_vanilla_items.add(ingredient["item"].split(":")[1])
			if "result" in recipe and "item" in recipe["result"]:
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
						with super_open(destination, "wb") as file:
							return file.write(response.content)
			# If all attempts failed
			warning(f"Failed to download texture for '{item}', please add it manually to '{destination}'")
			warning(f"Suggestion link: '{DOWNLOAD_VANILLA_ASSETS_SOURCE}'")

	# Multithread the download
	multithreading(download_item, used_vanilla_items, max_workers=min(32, len(used_vanilla_items)))

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

