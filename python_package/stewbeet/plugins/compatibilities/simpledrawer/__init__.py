""" 🗄️ SimpleDrawer compatibility, for compacting drawers. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, FunctionTag
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.ingredients import Ingr
from ....core.cls.item import Item
from ....core.cls.recipe import CraftingShapedRecipe, CraftingShapelessRecipe
from ....core.utils.io import set_json_encoder, write_function


# Get result count of an item
def get_result_count(item: str, ingr_to_seek: str) -> int:
	""" Get the result count of an item in a recipe
	Args:
		item:         Item to check recipes for
		ingr_to_seek: Ingredient to seek in the recipe
	"""
	if not (item and ingr_to_seek):
		return 9
	# A crafting recipe with a single ingredient, the ingot, gives the count one block decompresses into
	for recipe in Item.from_id(item).recipes:
		if len(recipe.get("ingredients", [])) != 1:
			continue
		ingredient: Ingr | None = (
			next(iter(recipe["ingredients"].values())) if recipe["type"] == CraftingShapedRecipe.type
			else recipe["ingredients"][0] if recipe["type"] == CraftingShapelessRecipe.type
			else None
		)
		if ingredient is not None and ingredient.to_id(add_namespace=False) == ingr_to_seek:
			return recipe["result_count"]
	return 9


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.compatibilities.simpledrawer'")
def beet_default(ctx: Context):
	""" Main entry point for the simpledrawer compatibility plugin.
	This plugin sets up SimpleDrawer compatibility for compacting drawers.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx

	# Get namespace
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	simpledrawer_materials: list[dict[str, str]] = [
		variants for item in Mem.definitions
		if item.endswith("_block") and (variants := material_variants(item)) is not None and len(variants) > 2
	]
	if not simpledrawer_materials:
		return

	json_file: JsonDict = {"values": [f"{ns}:calls/simpledrawer/material"]}
	ctx.data["simpledrawer"].function_tags["material"] = set_json_encoder(FunctionTag(json_file))
	content: str = ""
	for material in simpledrawer_materials:
		for variant, item in material.items():
			if variant != "material":
				content += (
					"execute unless score #success_material simpledrawer.io matches 1 "
					"if data storage simpledrawer:io item_material.components"
					f'."minecraft:custom_data".{ns}.{item} '
					f'run function {ns}:calls/simpledrawer/{material["material"]}/{variant}\n'
				)
	write_function(f"{ns}:calls/simpledrawer/material", content)
	for material in simpledrawer_materials:
		write_material_functions(ns, material)
	stp.debug("Special datapack compatibility done for SimpleDrawer's compacting drawer!")


def material_variants(block: str) -> dict[str, str] | None:
	""" The forms of a storage block's material: the block, the material's name, and its ingot and nugget when defined.

	A raw block's ingot is the raw material. None for a block with no smithed material.
	"""
	smithed_dict: JsonDict = Item.from_id(block).components.get("custom_data", {}).get("smithed", {}).get("dict", {})
	if not smithed_dict:
		return None
	material_base: str = next(iter(next(iter(smithed_dict.values())).keys()))
	variants: dict[str, str] = {"block": block}
	if block.startswith("raw_"):
		variants["material"] = "raw_" + material_base
		if f"raw_{material_base}" in Mem.definitions:
			variants["ingot"] = f"raw_{material_base}"
		return variants

	variants["material"] = material_base
	ingot_type: str | None = next(
		(ingot for ingot in (f"{material_base}_ingot", material_base, f"{material_base}_fragment") if ingot in Mem.definitions), None
	)
	if ingot_type:
		variants["ingot"] = ingot_type
	if f"{material_base}_nugget" in Mem.definitions:
		variants["nugget"] = f"{material_base}_nugget"
	return variants


def write_material_functions(ns: str, material: dict[str, str]) -> None:
	""" A function per form of the material telling SimpleDrawer its type, and the main one giving its conversions and items. """
	types_for_variants: dict[str, str] = {"block": "0", "ingot": "1", "nugget": "2"}
	material_base: str = material["material"]
	material_title: str = material_base.replace("_", " ").title()
	for variant in material:
		if variant != "material":
			write_function(f"{ns}:calls/simpledrawer/{material_base}/{variant}", (
				f"\nscoreboard players set #type simpledrawer.io {types_for_variants[variant]}\n"
				f"function {ns}:calls/simpledrawer/{material_base}/main\n"
			))

	ingot_in_block: int = get_result_count(material.get("ingot", ""), material.get("block", ""))
	nugget_in_ingot: int = get_result_count(material.get("nugget", ""), material.get("ingot", ""))
	content: str = f"""
# Set score of material found to 1
scoreboard players set #success_material simpledrawer.io 1

# Set the convert counts
scoreboard players set #ingot_in_block simpledrawer.io {ingot_in_block}
scoreboard players set #nugget_in_ingot simpledrawer.io {nugget_in_ingot}

# Set the material data
data modify storage simpledrawer:io material set value {{material: "{ns}.{material_base}", material_name:"{material_title}"}}

# Fill the NBT with your own items
"""
	for variant, item in material.items():
		if variant != "material":
			content += f"data modify storage simpledrawer:io material.{variant}.item set from storage {ns}:items all.{item}\n"
	write_function(f"{ns}:calls/simpledrawer/{material_base}/main", content)

