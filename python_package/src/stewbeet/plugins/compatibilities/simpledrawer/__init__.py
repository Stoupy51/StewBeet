
# Imports
from beet import Context, FunctionTag
from beet.core.utils import JsonDict
from stouputils.decorators import measure_time
from stouputils.io import super_json_dump
from stouputils.print import debug, progress

from ....core.__memory__ import Mem
from ....core.constants import RESULT_OF_CRAFTING
from ....core.ingredients import ingr_to_id
from ....core.utils.io import write_function


# Get result count of an item
def get_result_count(item: str, ingr_to_seek: str) -> int:
	""" Get the result count of an item in a recipe
	Args:
		item			(str):	Item to check recipes for
		ingr_to_seek	(str):	Ingredient to seek in the recipe
	"""
	if item and ingr_to_seek:

		# Get recipes
		definitions: dict[str, dict] = Mem.definitions
		recipes: list[dict] = definitions[item].get(RESULT_OF_CRAFTING, [])
		for recipe in recipes:			# If crafting shaped and only one ingredient, return the result count if the ingredient is the ingot item
			if recipe["type"] == "crafting_shaped" and len(recipe["ingredients"]) == 1:
				ingredient: dict = next(iter(recipe["ingredients"].values()))
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


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.compatibilities.simpledrawer'")
def beet_default(ctx: Context):
	""" Main entry point for the simpledrawer compatibility plugin.
	This plugin sets up SimpleDrawer compatibility for compacting drawers.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None:
		Mem.ctx = ctx

	# Get namespace
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# For each material block, collect materials and their variants
	simpledrawer_materials: list[dict[str, str]] = []
	for item, data in Mem.definitions.items():
		if item.endswith("_block"):
			variants: dict[str, str] = {"block": item}

			# Get material base
			smithed_dict: dict = data.get("custom_data", {}).get("smithed", {}).get("dict", {})
			if not smithed_dict:
				continue
			material_base: str = next(iter(next(iter(smithed_dict.values())).keys()))

			# If raw material block, add the ingot raw item if available
			if item.startswith("raw_"):
				variants["material"] = "raw_" + material_base
				if f"raw_{material_base}" in Mem.definitions:
					variants["ingot"] = f"raw_{material_base}"

			# Else, get the ingot material and the nugget form if any
			else:
				variants["material"] = material_base

				# Get ingot item if any
				ingot_types: list = [material_base, f"{material_base}_ingot", f"{material_base}_fragment"]
				ingot_type: str | None = None
				for ingot in ingot_types:
					if ingot in Mem.definitions:
						ingot_type = ingot
						break
				if ingot_type:
					variants["ingot"] = ingot_type

				# Get nugget if any
				if f"{material_base}_nugget" in Mem.definitions:
					variants["nugget"] = f"{material_base}_nugget"

			if len(variants) > 2:
				simpledrawer_materials.append(variants)

	# If any material block has variants, add the functions
	if simpledrawer_materials:

		# Link function tag
		json_file: JsonDict = {"values": [f"{ns}:calls/simpledrawer/material"]}
		tag: FunctionTag = FunctionTag(json_file)
		tag.encoder = super_json_dump
		ctx.data["simpledrawer"].function_tags["material"] = tag

		# Write material function
		content: str = ""
		for material in simpledrawer_materials:
			material_base = material["material"]
			for variant, item in material.items():
				if variant != "material":
					content += (
						"execute unless score #success_material simpledrawer.io matches 1 if data storage simpledrawer:io item_material.components"
						f'."minecraft:custom_data".{ns}.{item} run function {ns}:calls/simpledrawer/{material_base}/{variant}\n'
					)

		write_function(f"{ns}:calls/simpledrawer/material", content)

		# Make materials folders
		types_for_variants: dict[str, str] = {"block": "0", "ingot": "1", "nugget": "2"}
		for material in simpledrawer_materials:

			# Get material base
			material_base: str = material["material"]
			material_title: str = material_base.replace("_", " ").title()

			# For each variant, make a file
			for variant in material.keys():
				if variant != "material":
					content: str = f"scoreboard players set #type simpledrawer.io {types_for_variants[variant]}\nfunction {ns}:calls/simpledrawer/{material_base}/main"
					write_function(f"{ns}:calls/simpledrawer/{material_base}/{variant}", content)

			# Get ingot and nugget conversions if any
			ingot_in_block: int = get_result_count(material.get("ingot", ""), material.get("block", ""))
			nugget_in_ingot: int = get_result_count(material.get("nugget", ""), material.get("ingot", ""))

			# Make main function
			content: str = f"""
# Set score of material found to 1
scoreboard players set #success_material simpledrawer.io 1

# Set the convert counts
scoreboard players set #ingot_in_block simpledrawer.io {ingot_in_block}
scoreboard players set #nugget_in_ingot simpledrawer.io {nugget_in_ingot}

# Set the material data
data modify storage simpledrawer:io material set value {{material: "{ns}.{material_base}", material_name:'{material_title}'}}

# Fill the NBT with your own items
"""
			for variant, item in material.items():
				if variant != "material":
					content += f"data modify storage simpledrawer:io material.{variant}.item set from storage {ns}:items all.{item}\n"

			write_function(f"{ns}:calls/simpledrawer/{material_base}/main", content)

		# Debug message
		debug("Special datapack compatibility done for SimpleDrawer's compacting drawer!")

