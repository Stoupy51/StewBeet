
# Imports
import os
from pathlib import Path

import requests
import stouputils as stp
from beet import ProjectConfig, run_beet
from model_resolver import Render

from ...stewbeet.core.constants import (
	CUSTOM_BLOCK_VANILLA,
	DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE,
	OVERRIDE_MODEL,
	RESULT_OF_CRAFTING,
	USED_FOR_CRAFTING,
)
from ..utils.io import super_copy


# Generate iso renders for every item in the database
def generate_all_iso_renders(config: dict):
	database: dict[str, dict] = config['database']
	namespace: str = config['namespace']

	# Create the items folder
	path = config['manual_path'] + "/items"
	os.makedirs(f"{path}/{namespace}", exist_ok = True)

	# For every item, get the model path and the destination path
	for_model_resolver: dict[str, str] = {}
	for item, data in database.items():

		# Skip items that don't have models
		if not data.get("item_model"):
			continue

		# If it's not a block, simply copy the texture
		try:
			if data["id"] == CUSTOM_BLOCK_VANILLA:
				raise ValueError()
			if not os.path.exists(f"{path}/{namespace}/{item}.png") or not config['cache_manual_assets']:
				if data.get(OVERRIDE_MODEL, None) != {}:
					source: str = f"{config['assets_folder']}/textures/{item}.png"
					if os.path.exists(source):
						super_copy(source, f"{path}/{namespace}/{item}.png")
					else:
						stp.warning(f"Missing texture for item '{item}', please add it manually to '{path}/{namespace}/{item}.png'")
		except ValueError:
			# Else, add the block to the model resolver list
			# Skip if item is already generated (to prevent OpenGL launching for nothing)
			if os.path.exists(f"{path}/{namespace}/{item}.png") and config['cache_manual_assets']:
				continue

			# Add to the model resolver queue
			rp_path = f"{namespace}:item/{item}"
			dst_path = f"{path}/{namespace}/{item}.png"
			for_model_resolver[rp_path] = dst_path

	# Launch model resolvers for remaining blocks
	if len(for_model_resolver) > 0:
		load_dir = Path(config['build_resource_pack'])

		## Model Resolver v0.12.0
		# model_resolver_main(
		# 	render_size = config['opengl_resolution'],
		# 	load_dir = load_dir,
		# 	output_dir = None,	# type: ignore
		# 	use_cache = False,
		# 	minecraft_version = "latest",
		# 	__special_filter__ = for_model_resolver	# type: ignore
		# )

		## Model Resolver v1.3.0
		beet_config = ProjectConfig(
			output=None,
			resource_pack={"load": load_dir, "name": load_dir.name}, # type: ignore
			meta={"model_resolver": {"dont_merge_datapack": True, "use_cache": True}}
		)

		stp.debug(f"Generating iso renders for {len(for_model_resolver)} items, this may take a while...")
		with run_beet(config=beet_config, cache=True) as ctx:
			render = Render(ctx)
			for rp_path, dst_path in for_model_resolver.items():
				render.add_model_task(rp_path, path_save=dst_path)
			render.run()
		stp.debug("Generated iso renders for all items")

	## Copy every used vanilla items
	# Get every used vanilla items
	used_vanilla_items = set()
	for data in database.values():
		all_crafts: list[dict] = list(data.get(RESULT_OF_CRAFTING,[]))
		all_crafts += list(data.get(USED_FOR_CRAFTING,[]))
		for recipe in all_crafts:
			ingredients = []
			if "ingredients" in recipe:
				ingredients = recipe["ingredients"]
				if isinstance(ingredients, dict):
					ingredients = ingredients.values()
			elif "ingredient" in recipe:
				ingredients = [recipe["ingredient"]]
			for ingredient in ingredients:
				if "item" in ingredient:
					used_vanilla_items.add(ingredient["item"].split(":")[1])
			if "result" in recipe and "item" in recipe["result"]:
				used_vanilla_items.add(recipe["result"]["item"].split(":")[1])
		pass

	# Download all the vanilla textures from the wiki
	def download_item(item: str):
		destination = f"{path}/minecraft/{item}.png"
		if not (os.path.exists(destination) and config['cache_manual_assets']):	# If not downloaded yet or not using cache
			response = requests.get(f"{DOWNLOAD_VANILLA_ASSETS_RAW}/item/{item}.png")
			if response.status_code == 200:
				with stp.super_open(destination, "wb") as file:
					file.write(response.content)
			else:
				stp.warning(f"Failed to download texture for item '{item}', please add it manually to '{destination}'")
				stp.warning(f"Suggestion link: '{DOWNLOAD_VANILLA_ASSETS_SOURCE}'")

	# Multithread the download
	stp.multithreading(download_item, used_vanilla_items, max_workers=min(32, len(used_vanilla_items)))

