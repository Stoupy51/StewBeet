
# ruff: noqa: E501
# Imports
from beet.core.utils import JsonDict
from stouputils.decorators import simple_cache

from ...core.__memory__ import Mem
from ...core.constants import PULVERIZING, RESULT_OF_CRAFTING
from ...core.ingredients import (
	ALL_RECIPES_TYPES,
	FURNACES_RECIPES_TYPES,
	ingr_repr,
	ingr_to_id,
)
from .shared_import import FURNACE_FONT, MINING_FONT, PULVERIZING_FONT, SHAPED_2X2_FONT, SHAPED_3X3_FONT, STONECUTTING_FONT


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

	# Get all ingredients to the dictionary and map each ingredient to a key, preserving order
	next_key: str = "A"
	ingredient_to_key: dict[str, str] = {}
	ordered_keys: list[str] = []

	for ingr in shapeless_ingredients:
		ingr_str = str(ingr)

		# Check if we've already seen this ingredient
		if ingr_str not in ingredient_to_key:
			# New ingredient, assign it the next key
			ingredient_to_key[ingr_str] = next_key
			shaped_recipe["ingredients"][next_key] = ingr
			next_key = chr(ord(next_key) + 1)

		# Record the key for this position (preserving order)
		ordered_keys.append(ingredient_to_key[ingr_str])

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
	elif len(shaped_recipe["ingredients"]) == 3 and total_items == 9:

		# Get the key for the item that is less frequent
		len_A: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["A"])])
		len_B: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["B"])])
		len_C: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["C"])])
		small: str = "A" if len_A < len_B and len_A < len_C else "B" if len_B < len_C else "C"
		other_1: str = "B" if small == "A" else "A" if small == "C" else "C"
		other_2: str = "C" if small == "A" else "C" if small == "B" else "B"
		shaped_recipe["shape"] = [other_1+other_2+other_1, other_2+small+other_2, other_1+other_2+other_1]
	else:
		# Determine the grid size based on total items
		# Perfect squares: 1, 4, 9 -> use sqrt as col_size
		# Otherwise: use 3 for <=9 items, 2 for <=4 items
		import math
		sqrt_items = int(math.sqrt(total_items))
		if sqrt_items * sqrt_items == total_items:
			# Perfect square
			col_size = sqrt_items
		elif total_items <= 4:
			col_size = 2
		else:
			col_size = 3

		# Build the shape preserving the original order
		shaped_recipe["shape"] = ["".join(ordered_keys[i:i + col_size]) for i in range(0, len(ordered_keys), col_size)]

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
	elif craft["type"] == "stonecutting":
		return STONECUTTING_FONT
	elif craft["type"] == "mining":
		return MINING_FONT
	else:
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
		if any(craft["type"] in t for t in ALL_RECIPES_TYPES):
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

