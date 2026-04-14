
# Imports
import os
import shutil
from typing import cast

import requests
import stouputils as stp
from beet import Model
from stouputils.typing import JsonDict
from model_resolver.render import Render

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from ...core.constants import (
	DOWNLOAD_VANILLA_ASSETS_RAW,
	DOWNLOAD_VANILLA_ASSETS_SOURCE,
	DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW,
)
from .shared_import import SharedMemory


def download_item(path: str, item: str, cache_assets: bool, destination: str = "") -> None:
	""" Download a single vanilla item texture from the wiki. """
	if not destination:
		destination = f"{path}/minecraft/{item}.png"
	if os.path.exists(destination) and cache_assets:
		return
	for base_link in (DOWNLOAD_VANILLA_ASSETS_SPECIAL_RAW, DOWNLOAD_VANILLA_ASSETS_RAW):
		for folder in ["item", "block", "items"]:
			link: str = f"{base_link}/{folder}/{item}.png"
			response = requests.get(link)
			if response.status_code == 200:
				with stp.super_open(destination, "wb") as file:
					file.write(response.content)
				return
	stp.warning(f"Failed to download texture for '{item}', please add it manually to '{destination}'")
	stp.warning(f"Suggestion link: '{DOWNLOAD_VANILLA_ASSETS_SOURCE}'")


def build_model_resolver_queue(path: str, ns: str, cache_assets: bool) -> dict[str, str]:
	""" Build the queue of items that need iso renders generated. """
	for_model_resolver: dict[str, str] = {}
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)
		if not obj.components.get("item_model"):
			continue
		if os.path.exists(f"{path}/{ns}/{item}.png") and cache_assets:
			continue
		model: Model | None = Mem.ctx.assets[ns].models.get(f"item/{item}")
		rp_path = f"{ns}:item/{item}"
		dst_path = f"{path}/{ns}/{item}.png"
		if model is not None and model.get_content().get("textures", None) is not None:  # type: ignore
			for_model_resolver[rp_path] = dst_path
	return for_model_resolver


def run_model_resolver(for_model_resolver: dict[str, str]) -> None:
	""" Run the model resolver to generate iso renders for the given items. """
	any_atlas_used: bool = "before_format_73" in Mem.ctx.assets.overlays._wrapped.keys()  # type: ignore
	if any_atlas_used:
		Mem.ctx.assets["minecraft"].atlases["temporary_stewbeet"] = Mem.ctx.assets.overlays["before_format_73"]["minecraft"].atlases["blocks"]

	stp.debug(f"Generating iso renders for {len(for_model_resolver)} items, this may take a while...")
	render = Render(Mem.ctx)
	for rp_path, dst_path in for_model_resolver.items():
		render.add_model_task(rp_path, path_save=dst_path, animation_mode="one_file")
	render.run()
	stp.debug("Generated iso renders for all items")

	if any_atlas_used:
		del Mem.ctx.assets["minecraft"].atlases["temporary_stewbeet"]


def collect_used_vanilla_items() -> set[str]:
	""" Collect all vanilla items referenced in recipes across all definitions. """
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
	return used_vanilla_items


def download_vanilla_textures(path: str, used_vanilla_items: set[str], cache_assets: bool) -> None:
	""" Download vanilla item textures from the wiki using multithreading. """
	if not used_vanilla_items:
		return
	args = [(path, item, cache_assets) for item in used_vanilla_items]
	stp.multithreading(
		download_item,
		args,
		use_starmap=True,
		max_workers=min(32, len(used_vanilla_items))
	)

def copy_painting_textures(path: str, ns: str, cache_assets: bool) -> None:
	""" Download and copy painting textures for custom painting items. """
	last_painting_path: str = ""
	for item, data in Mem.definitions.items():
		if data["id"] == "minecraft:painting" and not data.get("item_model"):
			if not last_painting_path:
				last_painting_path = f"{path}/{ns}/{item}.png"
				download_item(path, "painting", cache_assets, last_painting_path)
			else:
				shutil.copy(last_painting_path, f"{path}/{ns}/{item}.png")


# Generate iso renders for every item in the definitions
def generate_all_iso_renders(override_cache_path: str | None = None, ignore_vanilla: bool = False, ignore_painting: bool = False):
	ns: str = Mem.ctx.project_id

	# Create the items folder
	path = override_cache_path or (SharedMemory.cache_path + "/items")
	os.makedirs(f"{path}/{ns}", exist_ok=True)

	cache_assets: bool = Mem.ctx.meta.get("stewbeet", {}).get("manual", {}).get("cache_assets", True)

	# Build queue and run model resolver
	for_model_resolver = build_model_resolver_queue(path, ns, cache_assets)
	if for_model_resolver:
		run_model_resolver(for_model_resolver)

	# Download vanilla textures used in recipes
	if not ignore_vanilla:
		used_vanilla_items = collect_used_vanilla_items()
		download_vanilla_textures(path, used_vanilla_items, cache_assets)

	# Handle custom painting textures
	if not ignore_painting:
		copy_painting_textures(path, ns, cache_assets)

