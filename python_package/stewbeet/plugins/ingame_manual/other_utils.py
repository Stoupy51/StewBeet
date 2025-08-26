
# ruff: noqa: E501
# Imports
from typing import cast

from beet.core.utils import JsonDict
from stouputils.decorators import simple_cache
from stouputils.print import error

from ...core.__memory__ import Mem
from ...core.constants import PULVERIZING, RESULT_OF_CRAFTING
from ...core.ingredients import (
	CRAFTING_RECIPES_TYPES,
	FURNACES_RECIPES_TYPES,
	SPECIAL_RECIPES_TYPES,
	ingr_repr,
	ingr_to_id,
)
from .shared_import import (
	FURNACE_FONT,
	PULVERIZING_FONT,
	SHAPED_2X2_FONT,
	SHAPED_3X3_FONT,
)


# Convert craft function
@simple_cache
def convert_shapeless_to_shaped(craft: JsonDict) -> JsonDict:
	""" Convert a shapeless craft to a shaped craft
	Args:
		craft (JsonDict): The craft to convert
	Returns:
		JsonDict: The craft converted
	"""
	shapeless_ingredients: list[str] = craft["ingredients"]
	total_items: int = len(shapeless_ingredients)
	shaped_recipe: JsonDict = {"type": "crafting_shaped", "result_count": craft["result_count"], "ingredients": {}}
	if craft.get("result"):
		shaped_recipe["result"] = craft["result"]

	# Get all ingredients to the dictionary
	next_key: str = "A"
	for ingr in shapeless_ingredients:
		key: str = next_key

		# Check if the ingredient is already in the shaped recipe, if so stop early
		for new_key, new_ingr in shaped_recipe["ingredients"].items():
			if str(ingr) == str(new_ingr):
				key = new_key	# This will skip the next condition below
				break

		# If the key is still the next key, it means it's a new ingredient, add it to the dictionary and update the next key
		if key == next_key:
			shaped_recipe["ingredients"][next_key] = ingr
			next_key = chr(ord(next_key) + 1)

	# Make the shape of the craft, with an exception when 2 materials to put one alone in the center
	if len(shaped_recipe["ingredients"]) == 2 and total_items in (5, 9):

		# Get the key for the item that is more frequent and the key for the other
		len_same: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["A"])])
		big: str = "A" if len_same > 1 else "B"
		other: str = "B" if big == "A" else "A"

		if total_items == 9:
			shaped_recipe["shape"] = [big*3, big+other+big, big*3]
		elif total_items == 5:
			shaped_recipe["shape"] = [f" {big} ", big+other+big, f" {big} "]
	else:

		# For each ingredient, add to the shape depending on the occurences
		shaped_recipe["shape"] = cast(list[str], [])
		for key, ingr in shaped_recipe["ingredients"].items():
			for ingr_craft in craft["ingredients"]:
				if str(ingr_craft) == str(ingr):
					shaped_recipe["shape"].append(key)

		# Fix the shape (ex: ["A","A","A","B","B","B","C","C","C"] -> ["AAA","BBB","CCC"])
		# ex 2: ["A","B","C","D"] -> ["AB","CD"]
		col_size = 3
		if len(shaped_recipe["shape"]) <= 4:
			col_size = 2
		ranged = range(0, len(shaped_recipe["shape"]), col_size)
		shaped_recipe["shape"] = ["".join(shaped_recipe["shape"][i:i + col_size]) for i in ranged]

	# Return the shaped craft
	return shaped_recipe


# Util function
@simple_cache
def high_res_font_from_craft(craft: JsonDict) -> str:
	if craft["type"] in FURNACES_RECIPES_TYPES:
		return FURNACE_FONT
	elif craft["type"] == "crafting_shaped":
		if len(craft["shape"]) == 3 or len(craft["shape"][0]) == 3:
			return SHAPED_3X3_FONT
		else:
			return SHAPED_2X2_FONT
	elif craft["type"] == PULVERIZING:
		return PULVERIZING_FONT
	else:
		error(f"Unknown craft type '{craft['type']}'")
		return ""

def remove_unknown_crafts(crafts: list[JsonDict]) -> list[JsonDict]:
	""" Remove crafts that are not recognized by the program
	Args:
		crafts (list[JsonDict]): The list of crafts
	Returns:
		list[JsonDict]: The list of crafts without unknown crafts
	"""
	supported_crafts: list[JsonDict] = []
	for craft in crafts:
		if craft["type"] in CRAFTING_RECIPES_TYPES or craft["type"] in FURNACES_RECIPES_TYPES or craft["type"] in SPECIAL_RECIPES_TYPES:
			supported_crafts.append(craft)
	return supported_crafts

# Generate USED_FOR_CRAFTING key like
def generate_otherside_crafts(item: str) -> list[JsonDict]:
	""" Generate the USED_FOR_CRAFTING key like
	Args:
		item (str): The item to generate the key for
	Returns:
		list[JsonDict]: ex: [{"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"chainmail": true}}}}},"result": {"item": "minecraft:chainmail_helmet","count": 1}}, ...]
	"""
	# Get all crafts that use the item
	crafts: list[JsonDict] = []
	for key, value in Mem.definitions.items():
		if key != item and value.get(RESULT_OF_CRAFTING):
			for craft in value[RESULT_OF_CRAFTING]:
				if ("ingredient" in craft and item == ingr_to_id(craft["ingredient"], False)) or \
					("ingredients" in craft and isinstance(craft["ingredients"], dict) and item in [ingr_to_id(x, False) for x in craft["ingredients"].values()]) or \
					("ingredients" in craft and isinstance(craft["ingredients"], list) and item in [ingr_to_id(x, False) for x in craft["ingredients"]]):
					# Convert craft, ex:
					# before:	chainmail_helmet	{"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"chainmail": true}}}}}}}
					# after:	chainmail			{"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"chainmail": true}}}}},"result": {"item": "minecraft:chainmail_helmet","count": 1}}
					craft_copy: JsonDict = craft.copy()
					craft_copy["result"] = ingr_repr(key, ns = Mem.ctx.project_id, count = craft["result_count"])
					crafts.append(craft_copy)
	return crafts

