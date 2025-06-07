"""
Handles generation of book components and content
"""
import os

import stouputils as stp
from PIL import Image

from ..utils.ingredients import ingr_to_id
from .image_utils import generate_high_res_font
from .shared_import import COMPONENTS_TO_INCLUDE, NONE_FONT, get_page_number


# Call the previous function
def high_res_font_from_ingredient(config: dict, ingredient: str|dict, count: int = 1) -> str:
	""" Generate the high res font to display in the manual for the ingredient
	Args:
		ingredient	(str|dict):	The ingredient, ex: "adamantium_fragment" or {"item": "minecraft:stick"} or {"components": {"custom_data": {"iyc": {"adamantium_fragment": true}}}}
		count		(int):		The count of the item
	Returns:
		str: The font to the generated texture
	"""
	# Decode the ingredient
	if isinstance(ingredient, dict):
		ingr_str: str = ingr_to_id(ingredient, add_namespace = True)
	else:
		ingr_str = ingredient

	# Get the item image
	if ':' in ingr_str:
		image_path = f"{config['manual_path']}/items/{ingr_str.replace(':', '/')}.png"
		if not os.path.exists(image_path):
			stp.error(f"Missing item texture at '{image_path}'")
		item_image = Image.open(image_path)
		ingr_str = ingr_str.split(":")[1]
	else:
		item_image = Image.open(f"{config['manual_path']}/items/{config['namespace']}/{ingr_str}.png")
	
	# Generate the high res font
	return generate_high_res_font(config, ingr_str, item_image, count)


# Convert ingredient to formatted JSON for book
def get_item_component(config: dict, ingredient: dict|str, only_those_components: list[str] = [], count: int = 1) -> dict:
	""" Generate item hover text for a craft ingredient
	Args:
		ingredient (dict|str): The ingredient
			ex: {'components': {'custom_data': {'iyc': {'adamantium_fragment': True}}}}
			ex: {'item': 'minecraft:stick'}
			ex: "adamantium_fragment"	# Only available for the datapack items
	Returns:
		dict: The text component
			ex: {"text":NONE_FONT,"color":"white","hover_event":{"action":"show_item","id":"minecraft:command_block", "components": {...}},"click_event":{"action":"change_page","value":"8"}}
			ex: {"text":NONE_FONT,"color":"white","hover_event":{"action":"show_item","id":"minecraft:stick"}}
	"""
	# Get the item id
	formatted: dict = {
		"text": NONE_FONT,
		"hover_event": {
			"action": "show_item",
			"id": "",  # Inline contents field
			"components": {}  # Will be added if needed
		}
	}

	if isinstance(ingredient, dict) and ingredient.get("item"):
		formatted["hover_event"]["id"] = ingredient["item"]
	else:
		# Get the item in the database
		if isinstance(ingredient, str):
			id = ingredient
			item = config['database'][ingredient]
		else:
			custom_data: dict = ingredient["components"]["minecraft:custom_data"]
			id = ingr_to_id(ingredient, add_namespace = False)
			if custom_data.get(config['namespace']):
				item = config['database'].get(id)
			else:
				ns = list(custom_data.keys())[0] + ":"
				for data in custom_data.values():
					item = config['external_database'].get(ns + list(data.keys())[0])
					if item:
						break
		if not item:
			stp.error("Item not found in database or external database: " + str(ingredient))
		
		# Copy id and components
		formatted["hover_event"]["id"] = item["id"].replace("minecraft:", "")
		components = {}
		if only_those_components:
			for key in only_those_components:
				if key in item:
					components[key] = item[key]
		else:
			for key, value in item.items():
				if key in COMPONENTS_TO_INCLUDE:
					components[key] = value
		formatted["hover_event"]["components"] = components

		# If item is from my datapack, get its page number
		page_number = get_page_number(id)
		if page_number != -1:
			formatted["click_event"] = {
				"action": "change_page",
				"page": page_number
			}
	
	# High resolution
	if config["manual_high_resolution"]:
		formatted["text"] = high_res_font_from_ingredient(config, ingredient, count)

	# Return
	return formatted

