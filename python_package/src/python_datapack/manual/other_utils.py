
# Imports
import stouputils as stp

from ...stewbeet.core.constants import PULVERIZING, RESULT_OF_CRAFTING
from ..utils.ingredients import (
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
@stp.simple_cache()
def convert_shapeless_to_shaped(craft: dict) -> dict:
	""" Convert a shapeless craft to a shaped craft
	Args:
		craft (dict): The craft to convert
	Returns:
		dict: The craft converted
	"""
	new_craft = {"type": "crafting_shaped", "result_count": craft["result_count"], "ingredients": {}}
	if craft.get("result"):
		new_craft["result"] = craft["result"]

	# Get all ingredients to the dictionary
	next_key = "A"
	for ingr in craft["ingredients"]:
		key = next_key
		for new_key, new_ingr in new_craft["ingredients"].items():
			if str(ingr) == str(new_ingr):
				key = new_key
				break

		if key == next_key:
			new_craft["ingredients"][next_key] = ingr
			next_key = chr(ord(next_key) + 1)

	# Make the shape of the craft, with an exception when 2 materials to put one alone in the center
	if len(new_craft["ingredients"]) == 2 and len(craft["ingredients"]) == 9:
		new_craft["shape"] = ["AAA","ABA","AAA"]
	else:

		# For each ingredient, add to the shape depending on the occurences
		new_craft["shape"] = []
		for key, ingr in new_craft["ingredients"].items():
			for ingr_craft in craft["ingredients"]:
				if str(ingr_craft) == str(ingr):
					new_craft["shape"].append(key)
		
		# Fix the shape (ex: ["A","A","A","B","B","B","C","C","C"] -> ["AAA","BBB","CCC"])
		# ex 2: ["A","B","C","D"] -> ["AB","CD"]
		col_size = 3
		if len(new_craft["shape"]) <= 4:
			col_size = 2
		ranged = range(0, len(new_craft["shape"]), col_size)
		new_craft["shape"] = ["".join(new_craft["shape"][i:i + col_size]) for i in ranged]
	
	# Return the shaped craft
	return new_craft


# Util function
@stp.simple_cache()
def high_res_font_from_craft(craft: dict) -> str:
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
		stp.error(f"Unknown craft type '{craft['type']}'")
		return ""

def remove_unknown_crafts(crafts: list[dict]) -> list[dict]:
	""" Remove crafts that are not recognized by the program
	Args:
		crafts (list[dict]): The list of crafts
	Returns:
		list[dict]: The list of crafts without unknown crafts
	"""
	supported_crafts = []
	for craft in crafts:
		if craft["type"] in CRAFTING_RECIPES_TYPES or craft["type"] in FURNACES_RECIPES_TYPES or craft["type"] in SPECIAL_RECIPES_TYPES:
			supported_crafts.append(craft)
	return supported_crafts

# Generate USED_FOR_CRAFTING key like
def generate_otherside_crafts(config: dict, item: str) -> list[dict]:
	""" Generate the USED_FOR_CRAFTING key like
	Args:
		item (str): The item to generate the key for
	Returns:
		list[dict]: ex: [{"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"chainmail": true}}}}},"result": {"item": "minecraft:chainmail_helmet","count": 1}}, ...]
	"""
	# Get all crafts that use the item
	crafts = []
	for key, value in config['database'].items():
		if key != item and value.get(RESULT_OF_CRAFTING):
			for craft in value[RESULT_OF_CRAFTING]:
				craft: dict = craft
				if ("ingredient" in craft and item == ingr_to_id(craft["ingredient"], False)) or \
					("ingredients" in craft and isinstance(craft["ingredients"], dict) and item in [ingr_to_id(x, False) for x in craft["ingredients"].values()]) or \
					("ingredients" in craft and isinstance(craft["ingredients"], list) and item in [ingr_to_id(x, False) for x in craft["ingredients"]]):
					# Convert craft, ex:
					# before:	chainmail_helmet	{"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"chainmail": true}}}}}}}
					# after:	chainmail			{"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"chainmail": true}}}}},"result": {"item": "minecraft:chainmail_helmet","count": 1}}
					craft_copy = craft.copy()
					craft_copy["result"] = ingr_repr(key, ns = config['namespace'], count = craft["result_count"])
					crafts.append(craft_copy)
	return crafts

