
# Imports
import os
from typing import Any

import stouputils as stp

from ...stewbeet.core.constants import CUSTOM_BLOCK_VANILLA, CUSTOM_ITEM_VANILLA, OVERRIDE_MODEL
from ..utils.io import super_copy, write_file


# Utility functions
def get_powered_texture(variants: list[str], side: str, on_off: str) -> str:
	if on_off != "":
		for texture in variants:
			if texture.endswith(side + on_off):
				return texture
	for texture in variants:
		if texture.endswith(side):
			return texture
	stp.error(f"Couldn't find texture for side '{side}' in '{variants}', consider adding missing texture or override the model")
	return ""

# Check if all models are in a string of any variant
def model_in_variants(models: list[str], variants: list[str]) -> bool:
	valid = True
	for model in models:
		if not any(model in x for x in variants):
			valid = False
			break
	return valid

# Function to handle item
def handle_item(config: dict, item: str, data: dict, used_textures: set|None = None, ignore_textures: bool = False) -> None:
	""" Generate custom models for an item or block

	Args:
		config			(dict):		The config dict containing all the data
		item			(str):		The item/block name, ex: "steel_ingot"
		data			(dict):		The item/block data, ex: {"id": CUSTOM_ITEM_VANILLA, "item_name": ...}
		used_textures	(set):		The set to add used textures to (if any)
		ignore_textures	(bool):		Whether to ignore textures or not (default: False, only used for the heavy workbench for NBT recipes)
	"""
	# If no item model, return
	if not data.get("item_model"):
		return

	# Initialize variables
	block_or_item: str = "item"
	if data.get("id") == CUSTOM_BLOCK_VANILLA or any((isinstance(x, str) and "block" in x) for x in data.get(OVERRIDE_MODEL, {}).values()):
		block_or_item = "block"
	dest_base_textu = f"{config['build_resource_pack']}/assets/{config['namespace']}/textures/item"
	overrides: dict = data.get(OVERRIDE_MODEL, {})
	textures_files: list[str] = config.get('textures_files', [])

	# Get powered states (if any)
	powered = [""]
	on_textures = []
	if not ignore_textures:
		for p in textures_files:
			if p.split("/")[-1].startswith(item) and p.endswith("_on.png"):
				powered = ["", "_on"]
				on_textures.append(p)

	# Generate its model file(s)
	for on_off in powered:
		dest_base_model = f"{config['build_resource_pack']}/assets/{config['namespace']}/models/item"
		content: dict = {}

		# Get all variants
		variants: list[str] = [x.replace(".png", "") for x in textures_files if "gui/" not in x and x.split("/")[-1].startswith(item)]

		if not ignore_textures and data.get(OVERRIDE_MODEL, None) != {}:
			# If it's a block
			if block_or_item == "block":

				# Get parent
				content = {"parent": "block/cube_all", "textures": {}}

				## Check in which variants state we are
				# If one texture, apply on all faces
				variants_without_on = [x for x in variants if "_on" not in x]
				if len(variants_without_on) == 1:
					content["textures"]["all"] = f"{config['namespace']}:item/" + get_powered_texture(variants, "", on_off)
				else:
					# Prepare models to check
					cake = ["bottom", "side", "top", "inner"]
					cube_bottom_top = ["bottom", "side", "top"]
					orientable = ["front", "side", "top"]
					cube_column = ["end", "side"]

					# Check cake model
					if model_in_variants(cake, variants):
						content["parent"] = "block/cake"
						for side in cake:
							content["textures"][side.replace("inner","inside")] = f"{config['namespace']}:item/" + get_powered_texture(variants, side, on_off)

						# Generate 6 models for each cake slice
						for i in range(1, 7):
							name: str = f"{item}_slice{i}"
							slice_content = {"parent": f"block/cake_slice{i}", "textures": content["textures"]}
							write_file(f"{dest_base_model}/{name}{on_off}.json", stp.super_json_dump(slice_content, max_level = 4))

					# Check cube_bottom_top model
					elif model_in_variants(cube_bottom_top, variants):
						content["parent"] = "block/cube_bottom_top"
						for side in cube_bottom_top:
							content["textures"][side] = f"{config['namespace']}:item/" + get_powered_texture(variants, side, on_off)

					# Check orientable model
					elif model_in_variants(orientable, variants):
						content["parent"] = "block/orientable"
						for side in orientable:
							content["textures"][side] = f"{config['namespace']}:item/" + get_powered_texture(variants, side, on_off)

					# Check cube_column model
					elif model_in_variants(cube_column, variants):
						content["parent"] = "block/cube_column"
						for side in cube_column:
							content["textures"][side] = f"{config['namespace']}:item/" + get_powered_texture(variants, side, on_off)

					# Else, if there are no textures override, show error
					elif not data.get(OVERRIDE_MODEL,{}).get("textures"):
						patterns = stp.super_json_dump({
							"cake": cake,
							"cube_bottom_top": cube_bottom_top,
							"orientable": orientable,
							"cube_column": cube_column
						}, max_level = 1)
						stp.error(f"Block '{item}' has invalid variants: {variants},\nconsider overriding the model or adding missing textures to match up one of the following patterns:\n{patterns}")

			# Else, it's an item
			else:

				# Get parent
				parent = "item/generated"
				data_id: str = data["id"]
				if data_id != CUSTOM_ITEM_VANILLA:
					parent = data_id.replace(':', ":item/")

				# Get textures
				textures = {"layer0": f"{config['namespace']}:item/{item}{on_off}"}
				content = {"parent": parent, "textures": textures}
				data_id = data_id.replace("minecraft:", "")

				# Check for leather armor textures
				if data_id.startswith("leather_"):
					textures["layer1"] = textures["layer0"]

				# Check for bow pulling textures, in order to write the items/bow.json file
				elif data_id.endswith("bow"):
					sorted_pull_variants: list[str] = sorted([v for v in variants if "_pulling_" in v], key=lambda x: int(x.split("_")[-1]))
					items_content: dict = {}
					if sorted_pull_variants:
						items_content["model"] = {
							"type": "minecraft:condition",
							"on_false": {
								"type": "minecraft:model",
								"model": f"{config['namespace']}:item/{item}"
							},
							"on_true": {
								"type": "minecraft:range_dispatch",
								"entries": [],
								"fallback": {
									"type": "minecraft:model",
									"model": f"{config['namespace']}:item/{item}_pulling_0"
								},
								"property": "minecraft:use_duration",
								"scale": 0.05
							},
							"property": "minecraft:using_item"
						}

						# Add override for each pulling state (pulling_0 = 0, pulling_1 = 0.65, pulling_2 = 0.9)
						for i, variant in enumerate(sorted_pull_variants):
							pull_content: dict = {"parent": parent,"textures": {"layer0": f"{config['namespace']}:item/{variant}"}}
							super_copy(f"{config['assets_folder']}/textures/{variant}.png", f"{dest_base_textu}/{variant}.png")
							write_file(f"{dest_base_model}/{item}_pulling_{i}.json", stp.super_json_dump(pull_content))

							if i < (len(sorted_pull_variants) - 1):
								pull: float = 0.65 + (0.25 * i)
								model: str = f"{config['namespace']}:item/{item}_pulling_{i + 1}"
								items_content["model"]["on_true"]["entries"].append({
									"model": {
										"type": "minecraft:model",
										"model": model
									},
									"threshold": pull
								})

						# Write the items/bow.json file
						write_file(f"{dest_base_model}/{item}{on_off}.json".replace("models/item", "items"), stp.super_json_dump(items_content, max_level = 4))

		# Add overrides
		for key, value in overrides.items():
			content[key] = value

		# If powered, check if the on state is in the variants and add it
		if on_off == "_on":
			for key, texture in content.get("textures", {}).items():
				texture: str
				if (texture.split("/")[-1] + on_off) in variants:
					content["textures"][key] = texture + on_off

		# Add used textures (ignore minecraft namespace)
		if used_textures is not None and content.get("textures") and not ignore_textures:
			for texture in content["textures"].values():
				if texture.startswith("minecraft:"):
					continue
				used_textures.add(texture)

		# Copy used textures
		if content.get("textures") and not ignore_textures:
			for texture in content["textures"].values():
				# Ignore if minecraft namespace
				if texture.startswith("minecraft:"):
					continue

				texture_path = "/".join(texture.split(":")[-1].split("/")[1:])	# Remove namespace and block/item
				source = f"{config['assets_folder']}/textures/{texture_path}.png"
				destination = f"{dest_base_textu}/{texture_path}.png"
				try:
					super_copy(source, destination)
					if os.path.exists(source + ".mcmeta"):
						super_copy(source + ".mcmeta", destination + ".mcmeta")
				except FileNotFoundError:
					stp.error(f"Texture '{source}' not found")

		# Write content if not empty
		if data.get(OVERRIDE_MODEL, None) != {}:
			dump: str = stp.super_json_dump(content, max_level = 4)
		else:
			dump: str = "{}\n"
		item_model_path: str = f"{dest_base_model}/{item}{on_off}.json"
		write_file(item_model_path, dump)
		config["rendered_item_models"].add(data["item_model"])

		# Generate the json file required in items/
		if not data["id"].endswith("bow"):
			model_path: str = item_model_path.replace("models/item", "items")
			items_model = {"model": {"type": "minecraft:model", "model": f"{config['namespace']}:item/{item}{on_off}"}}
			write_file(model_path, stp.super_json_dump(items_model, max_level = 4))



def main(config: dict):
	namespace: str = config["namespace"]
	database: dict[str, Any] = config["database"]
	config["rendered_item_models"] = set()

	# For each item, handle it
	used_textures: set[str] = set()
	for item, data in database.items():
		item_model: str = data.get("item_model", "")
		if (item_model not in config["rendered_item_models"] and item_model.startswith(namespace)):
			handle_item(config, item, data, used_textures)

	# Make warning for missing textures
	warns = []
	for texture in used_textures:
		path = f"{config['assets_folder']}/textures/" + "/".join(texture.split("/")[1:]) + ".png"
		if not os.path.exists(path):
			warns.append(f"Texture '{path}' not found")
	if warns:
		stp.warning("The following textures are used but missing:\n" + "\n".join(sorted(warns)))

