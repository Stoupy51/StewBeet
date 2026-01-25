
# Imports
from __future__ import annotations

from typing import cast

import stouputils as stp
from beet.core.utils import JsonDict, TextComponent
from box import Box

from ..__memory__ import Mem
from ..cls.external_item import ExternalItem
from ..cls.item import Item
from ..utils.io import convert_to_serializable


# Add item model component
def add_item_model_component(black_list: list[str] | None = None) -> None:
	""" Add an item model component to all items in the definitions.

	Args:
		black_list			(list[str]):	The list of items to ignore.
		ignore_paintings	(bool):			Whether to ignore items that are paintings (have PAINTING_DATA).
	"""
	if black_list is None:
		black_list = []
	for item, data in Mem.definitions.items():
		if isinstance(data, Item):
			data = data.components
		if item in black_list or data.get("item_model", None) is not None:
			continue
		data["item_model"] = f"{Mem.ctx.project_id}:{item}"
	return

# Add item name and lore
def add_item_name_and_lore_if_missing(is_external: bool = False, black_list: list[str] | None = None) -> None:
	""" Add item name and lore to all items in the definitions if they are missing.

	Args:
		is_external	(bool):				Whether the definitions is the external one or not (meaning the namespace is in the item name).
		black_list	(list[str]):		The list of items to ignore.
	"""
	# Load the source lore
	if black_list is None:
		black_list = []
	source_lore: TextComponent = Mem.ctx.meta.get("stewbeet", {}).get("source_lore", {})

	# For each item, add item name and lore if missing (if not in black_list)
	defs = Mem.external_definitions if is_external else Mem.definitions
	for item, data in defs.items():
		if item in black_list:
			continue
		if isinstance(data, Item | ExternalItem):
			data = data.components

		# Add item name if none
		if not data.get("item_name"):
			if not is_external:
				item_str: str = item.replace("_"," ").title()
			else:
				item_str: str = item.split(":")[-1].replace("_"," ").title()
			data["item_name"] = {"text": item_str}	# Use a TextComponent to allow auto.lang_file to work properly

		# Apply namespaced lore if none
		if not data.get("lore"):
			data["lore"] = cast(list[TextComponent], [])

		# If item is not external,
		if not is_external:

			# Add the source lore ONLY if not already present
			if source_lore not in data["lore"]:
				data["lore"].append(source_lore)

		# If item is external, add the source lore to the item lore (without ICON)
		else:
			# Extract the namespace
			titled_namespace: str = item.split(":")[0].replace("_"," ").title()

			# Create the new namespace lore with the titled namespace
			new_source_lore: JsonDict = {"text": titled_namespace, "italic": True, "color": "blue"}

			# Add the namespace lore ONLY if not already present
			if new_source_lore not in data["lore"]:
				data["lore"].append(new_source_lore)
	return

# Add private custom data for namespace
def add_private_custom_data_for_namespace(is_external: bool = False, black_list: list[str] | None = None) -> None:
	""" Add private custom data for namespace to all items in the definitions if they are missing.

	Args:
		is_external	(bool):				Whether the definitions is the external one or not (meaning the namespace is in the item name).
		black_list	(list[str]):		The list of items to ignore.
	"""
	if black_list is None:
		black_list = []
	defs = Mem.external_definitions if is_external else Mem.definitions
	for item, data in defs.items():
		if item in black_list:
			continue
		if isinstance(data, Item | ExternalItem):
			data = data.components
		if not data.get("custom_data"):
			data["custom_data"] = cast(JsonDict, {})
		if is_external and ":" in item:
			ns, id = item.split(":")
		else:
			ns, id = Mem.ctx.project_id, item
		if not data["custom_data"].get(ns):
			data["custom_data"][ns] = {}
		data["custom_data"][ns][id] = True
	return

# Smithed ignore convention
def add_smithed_ignore_vanilla_behaviours_convention() -> None:
	""" Add smithed convention to all items in the definitions if they are missing.

	Refer to https://wiki.smithed.dev/conventions/tag-specification/#custom-items for more information.
	"""
	for data in Mem.definitions.values():
		if isinstance(data, Item):
			data = data.components
		data["custom_data"] = Box(data.get("custom_data", {}), default_box=True, default_box_attr={}, default_box_create_on_get=True)
		data["custom_data"].smithed.ignore.functionality = True # pyright: ignore[reportUnknownMemberType]
		data["custom_data"].smithed.ignore.crafting = True # pyright: ignore[reportUnknownMemberType]

# Set manual components
def set_manual_components(white_list: list[str]) -> None:
	""" Override the components to include in the manual when hovering items.

	Args:
		white_list	(list[str]):	The list of components to include.
	"""
	if not white_list:
		return
	from ...plugins.ingame_manual.shared_import import SharedMemory
	SharedMemory.components_to_include = white_list

# Export all definitions to JSON
def export_all_definitions_to_json(file_name: str, is_external: bool = False, verbose: bool = True) -> None:
	""" Export all definitions to a single json file for debugging purposes.

	Args:
		file_name	(str):	The name of the file to export to.
		is_external	(bool):	Whether to export external definitions or not.
		verbose		(bool):	Whether to print a debug message or not.
	"""
	# Convert everything to fully serializable dicts
	definitions_copy: dict[str, JsonDict] = {}
	defs = Mem.external_definitions if is_external else Mem.definitions
	for item, data in defs.items():
		definitions_copy[item] = convert_to_serializable(data)

		# Create a copy of the definitions without OVERRIDE_MODEL key
		if "override_model" in definitions_copy[item]:
			del definitions_copy[item]["override_model"]

	# Export definitions to JSON for debugging generation
	stp.json_dump(definitions_copy, file_name, max_level=3)
	if verbose:
		stp.debug(f"Mem.definitions exported to '{stp.relative_path(file_name)}'")

