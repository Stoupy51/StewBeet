
# Imports
import stouputils as stp

from ...stewbeet.core.constants import RESULT_OF_CRAFTING
from ..utils.ingredients import ingr_to_id
from ..utils.io import write_file


# Get result count of an item
def get_result_count(config: dict, item: str, ingr_to_seek: str) -> int:
	""" Get the result count of an item in a recipe
	Args:
		config			(dict):	Configuration
		item			(str):	Item to check recipes for
		ingr_to_seek	(str):	Ingredient to seek in the recipe
	"""
	if item and ingr_to_seek:

		# Get recipes
		database: dict[str, dict] = config["database"]
		recipes: list[dict] = database[item].get(RESULT_OF_CRAFTING, [])
		for recipe in recipes:

			# If crafting shaped and only one ingredient, return the result count if the ingredient is the ingot item
			if recipe["type"] == "crafting_shaped" and len(recipe["ingredients"]) == 1:
				ingredient: dict = list(recipe["ingredients"].values())[0]
				ingr_str: str = ingr_to_id(ingredient, add_namespace = False)
				if ingr_str == ingr_to_seek:
					return recipe["result_count"]

			# If crafting shapeless and only one ingredient, return the result count if the ingredient is the ingot item
			elif recipe["type"] == "crafting_shapeless" and len(recipe["ingredients"]) == 1:
				ingredient: dict = recipe["ingredients"][0]
				ingr_str: str = ingr_to_id(ingredient, add_namespace = False)
				if ingr_str == ingr_to_seek:
					return recipe["result_count"]
	return 9

# Main function
def main(config: dict):
	database: dict[str, dict] = config["database"]
	namespace: str = config["namespace"]

	# For each material block,
	simpledrawer_materials: list[dict[str, str]] = []
	for item, data in database.items():
		if item.endswith("_block"):
			variants: dict[str, str] = {"block": item}

			# Get material base
			smithed_dict: dict = data.get("custom_data", {}).get("smithed", {}).get("dict", {})
			if not smithed_dict:
				continue
			material_base: str = list(list(smithed_dict.values())[0].keys())[0]

			# If raw material block, add the ingot raw item if available
			if item.startswith("raw_"):
				variants["material"] = "raw_" + material_base
				if f"raw_{material_base}" in database:
					variants["ingot"] = f"raw_{material_base}"
			
			# Else, get the ingot material and the nugget form if any
			else:
				variants["material"] = material_base

				# Get ingot item if any
				ingot_types: list = [material_base, f"{material_base}_ingot", f"{material_base}_fragment"]
				ingot_type: str | None = None
				for ingot in ingot_types:
					if ingot in database:
						ingot_type = ingot
						break
				if ingot_type:
					variants["ingot"] = ingot_type
				
				# Get nugget if any
				if f"{material_base}_nugget" in database:
					variants["nugget"] = f"{material_base}_nugget"
			
			if len(variants) > 2:
				simpledrawer_materials.append(variants)
	
	# If any material block has variants, add the functions
	if simpledrawer_materials:

		# Link function tag
		path: str = f"{config['build_datapack']}/data/simpledrawer/tags/function/material.json"
		json_file: dict = {"values": [f"{namespace}:calls/simpledrawer/material"]}
		write_file(path, stp.super_json_dump(json_file))
		
		# Write material function
		path: str = f"{config['build_datapack']}/data/{namespace}/function/calls/simpledrawer/material.mcfunction"
		content: str = ""
		for material in simpledrawer_materials:
			material_base = material["material"]
			for variant, item in material.items():
				if variant != "material":
					content += f'execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components."minecraft:custom_data".{namespace}.{item} run function {namespace}:calls/simpledrawer/{material_base}/{variant}\n'
		write_file(path, content)

		# Make materials folders
		types_for_variants: dict[str, str] = {"block": "0", "ingot": "1", "nugget": "2"}
		for material in simpledrawer_materials:

			# Get material base
			material_base: str = material["material"]
			material_title: str = material_base.replace("_", " ").title()
			material_folder: str = f"{config['build_datapack']}/data/{namespace}/function/calls/simpledrawer/{material_base}"

			# For each variant, make a file
			for variant, item in material.items():
				if variant != "material":
					path: str = f"{material_folder}/{variant}.mcfunction"
					content: str = f"scoreboard players set #type simpledrawer.io {types_for_variants[variant]}\nfunction {namespace}:calls/simpledrawer/{material_base}/main"
					write_file(path, content)

			# Get ingot and nugget conversions if any
			ingot_in_block: int = get_result_count(config, material.get("ingot", ""), material.get("block", ""))
			nugget_in_ingot: int = get_result_count(config, material.get("nugget", ""), material.get("ingot", ""))

			# Make main function
			path: str = f"{material_folder}/main.mcfunction"
			content: str = f"""
# Set score of material found to 1
scoreboard players set #success_material simpledrawer.io 1

# Set the convert counts
scoreboard players set #ingot_in_block simpledrawer.io {ingot_in_block}
scoreboard players set #nugget_in_ingot simpledrawer.io {nugget_in_ingot}

# Set the material data
data modify storage simpledrawer:io material set value {{material: "{namespace}.{material_base}", material_name:'{material_title}'}}

# Fill the NBT with your own items
"""
			for variant, item in material.items():
				if variant != "material":
					content += f"data modify storage simpledrawer:io material.{variant}.item set from storage {namespace}:items all.{item}\n"
			write_file(path, content)

		# Final print
		stp.debug("Special datapack compatibility done for SimpleDrawer's compacting drawer!")

