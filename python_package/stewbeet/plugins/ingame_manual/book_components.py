"""
Handles generation of book components and content
"""
import os

import stouputils as stp
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.ingredients import Ingr
from ...core.cls.item import Item
from .image_utils import generate_high_res_font
from .shared_import import NONE_FONT, SharedMemory, get_page_number


# Call the previous function
def high_res_font_from_ingredient(ingredient: str | Ingr, count: int = 1) -> str:
	""" Generate the high res font to display in the manual for the ingredient

	Args:
		ingredient	(str|dict):	The ingredient, ex: "adamantium_fragment" or {"item": "minecraft:stick"} or {"components": {"custom_data": {"iyc": {"adamantium_fragment": true}}}}
		count		(int):		The count of the item
	Returns:
		str: The font to the generated texture
	"""
	# Decode the ingredient
	if isinstance(ingredient, dict):
		ingr_str: str = Ingr(ingredient).to_id(add_namespace=True)
	else:
		ingr_str = ingredient

	# Get the item image
	if ':' in ingr_str:
		image_path = f"{SharedMemory.cache_path}/items/{ingr_str.replace(':', '/')}.png"
		if not os.path.exists(image_path):
			stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
			item_image = Image.new("RGBA", (16, 16), (255, 255, 255, 0))  # Placeholder image
		else:
			item_image = Image.open(image_path)
		ingr_str = ingr_str.split(":")[1]
	else:
		path: str = f"{SharedMemory.cache_path}/items/{Mem.ctx.project_id}/{ingr_str}.png"
		if not os.path.exists(path):
			stp.warning(f"Missing texture at '{path}', using placeholder texture")
			item_image = Image.new("RGBA", (16, 16), (255, 255, 255, 0))  # Placeholder image
		else:
			item_image = Image.open(path)

	# Generate the high res font
	return generate_high_res_font(ingr_str, item_image, count)


# Convert ingredient to formatted JSON for book
def get_item_component(ingredient: str | Ingr, only_those_components: list[str] | None = None, count: int = 1, add_change_page: bool = True) -> JsonDict:
	""" Generate item hover text for a craft ingredient
	Args:
		ingredient (dict|str): The ingredient
			ex: {'components': {'custom_data': {'iyc': {'adamantium_fragment': True}}}}
			ex: {'item': 'minecraft:stick'}
			ex: "adamantium_fragment"	# Only available for the datapack items
	Returns:
		TextComponent:
			ex: {"text":NONE_FONT,"color":"white","hover_event":{"action":"show_item","id":"minecraft:command_block", "components": {...}},"click_event":{"action":"change_page","value":"8"}}
			ex: {"text":NONE_FONT,"color":"white","hover_event":{"action":"show_item","id":"minecraft:stick"}}
	"""
	if only_those_components is None or SharedMemory.use_dialog > 0:
		only_those_components = []

	# Get the item id
	formatted: TextComponent = {
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
		# Get the item in the definitions
		obj: Item | None = None
		if isinstance(ingredient, str):
			id = ingredient
			obj = Item.from_id(ingredient)
		else:
			ingredient = Ingr(ingredient)
			custom_data: JsonDict = ingredient["components"]["minecraft:custom_data"]
			id = ingredient.to_id(add_namespace=False)
			if custom_data.get(Mem.ctx.project_id):
				if id in Mem.definitions:
					obj = Item.from_id(id)
			else:
				ns = next(iter(custom_data.keys())) + ":"
				for data in custom_data.values():
					item_id = ns + next(iter(data.keys()))
					if item_id not in Mem.external_definitions:
						continue
					obj = Item.from_id(item_id)
					break
		if not obj:
			stp.error("Item not found in definitions or external definitions: " + str(ingredient))
			return formatted

		# Copy id and components
		formatted["hover_event"]["id"] = obj.base_item.replace("minecraft:", "")
		components: JsonDict = {}
		if only_those_components:
			for key in only_those_components:
				if key in obj.components:
					components[key] = obj.components[key]
		elif not SharedMemory.use_dialog > 0:
			for key, value in obj.components.items():
				if key in SharedMemory.components_to_include:
					components[key] = value
		else:
			for key, value in obj.components.items():
				components[key] = value
		formatted["hover_event"]["components"] = components

		# If item is from my datapack, get its page number
		if add_change_page:
			page_number = get_page_number(id)
			if page_number != -1:
				formatted["click_event"] = {
					"action": "change_page",
					"page": page_number
				}

	# High resolution
	if SharedMemory.high_resolution:
		formatted["text"] = high_res_font_from_ingredient(ingredient, count)

	# Return
	return formatted

