
# Imports
from __future__ import annotations

import stouputils as stp
from beet.core.utils import JsonDict, TextComponent

from ..__memory__ import Mem


# Utility functions
@stp.simple_cache
def text_component_to_str(tc: TextComponent) -> str:
	""" Convert a TextComponent to a string
	Args:
		tc (TextComponent): The TextComponent to convert
	Returns:
		str: The converted string
	"""
	if isinstance(tc, str):
		return tc
	elif isinstance(tc, list):
		result: str = ""
		for part in tc:
			result += text_component_to_str(part)
		return result
	result: str = ""
	if tc.get("text"):
		result += tc["text"]
	if tc.get("extra"):
		for extra in tc["extra"]:
			result += text_component_to_str(extra)
	return result

@stp.simple_cache
def item_id_to_text_component(item_id: str, use_default: bool = True) -> TextComponent:
	""" Get the TextComponent from an item id

	Args:
		item_id (str): The item id, ex: "minecraft:stick" or "iyc:adamantium_ingot"
		use_default (bool): Whether to use the default prettified string if no TextComponent is found
	Returns:
		str: The TextComponent of the item, ex: "Stick" or {"text":"Adamantium Ingot"}
	"""
	if ":" not in item_id:
		item_id = f"{Mem.ctx.project_id}:{item_id}"

	# Internal definitions
	ns, id = item_id.split(":")
	from ..cls.item import Item
	if ns == Mem.ctx.project_id and id in Mem.definitions:
		definition = Item.from_id(id)
		components: JsonDict = definition.components

		# If jukebox_playable is present, search for item_name in custom_data
		if "jukebox_playable" in components:
			possible_item_name: TextComponent = components.get("custom_data", {}).get("smithed", {}).get("dict", {}).get("record", {}).get("item_name", "")
			if possible_item_name:
				return possible_item_name

		# Regular components
		for component in ("item_name", "custom_name"):
			if components.get(component):
				return components[component]

	# External definitions
	if item_id in Mem.external_definitions:
		ext_definition = Item.from_id(item_id)
		components: JsonDict = ext_definition.components

		# If jukebox_playable is present, search for item_name in custom_data
		if "jukebox_playable" in components:
			possible_item_name: TextComponent = components.get("custom_data", {}).get("smithed", {}).get("dict", {}).get("record", {}).get("item_name", "")
			if possible_item_name:
				return possible_item_name

		# Regular components
		for component in ("item_name", "custom_name"):
			if components.get(component):
				return components[component]

	# Default: prettify the id
	if use_default:
		return id.replace("_", " ").title()
	return ""

@stp.simple_cache
def item_id_to_name(item_id: str) -> str:
	""" Get the name from an item id

	Args:
		item_id (str): The item id, ex: "minecraft:stick" or "iyc:adamantium_ingot"
	Returns:
		str: The name of the item, ex: "Stick" or "Adamantium Ingot"
	"""
	return text_component_to_str(item_id_to_text_component(item_id))

