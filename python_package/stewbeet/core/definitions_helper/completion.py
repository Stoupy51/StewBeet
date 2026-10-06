
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import stouputils as stp
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ..__memory__ import Mem


# Add item model component
def add_item_model_component(black_list: list[str] | None = None) -> None:
	""" Add an item model component to all items in the definitions.

	Args:
		black_list:       The list of items to ignore.
		ignore_paintings: Whether to ignore items that are paintings (have PAINTING_DATA).
	"""
	if black_list is None:
		black_list = []
	for item, obj in Mem.definitions.items():
		data = obj.components
		if item in black_list or data.get("item_model", None) is not None:
			continue
		data["item_model"] = obj.generated_item_model
	return

# Add item name and lore
def add_item_name_and_lore_if_missing(is_external: bool = False, black_list: list[str] | None = None) -> None:
	""" Add item name and lore to all items in the definitions if they are missing.

	Args:
		is_external: Whether the definitions is the external one or not (meaning the namespace is in the item name).
		black_list:  The list of items to ignore.
	"""
	source_lore: TextComponent = Mem.ctx.meta.get("stewbeet", {}).get("source_lore", {})
	defs = Mem.external_definitions if is_external else Mem.definitions
	for item, data in defs.items():
		if item in (black_list or []):
			continue
		components = data.components

		# A TextComponent rather than a string, so auto.lang_file can translate it
		if not components.get("item_name"):
			components["item_name"] = {"text": item.split(":")[-1].replace("_"," ").title()}

		# An external item names the pack it comes from, without the project's icon
		item_lore: TextComponent = (
			{"text": item.split(":")[0].replace("_"," ").title(), "italic": True, "color": "blue"} if is_external else source_lore
		)
		lore: list[TextComponent] = components.setdefault("lore", [])
		if item_lore not in lore:
			lore.append(item_lore)

# Add private custom data for namespace
def add_private_custom_data_for_namespace(is_external: bool = False, black_list: list[str] | None = None) -> None:
	""" Add private custom data for namespace to all items in the definitions if they are missing.

	Args:
		is_external: Whether the definitions is the external one or not (meaning the namespace is in the item name).
		black_list:  The list of items to ignore.
	"""
	if black_list is None:
		black_list = []
	defs = Mem.external_definitions if is_external else Mem.definitions
	for item, data in defs.items():
		if item in black_list:
			continue
		data = data.components
		custom_data: JsonDict = data.setdefault("custom_data", {})
		if is_external and ":" in item:
			ns, id = item.split(":")
		else:
			ns, id = Mem.ctx.project_id, item
		custom_data.setdefault(ns, {})
		custom_data[ns][id] = True

		# Smithed item convention (smithed:{id:"ns:id",origin:"ns"})
		smithed: JsonDict = custom_data.setdefault("smithed", {})
		smithed.setdefault("id", f"{ns}:{id}")
		smithed.setdefault("origin", ns)
	return

# Smithed ignore convention
def add_smithed_ignore_vanilla_behaviours_convention() -> None:
	""" Add smithed convention to all items in the definitions if they are missing.

	Refer to https://wiki.smithed.dev/conventions/tag-specification/#custom-items for more information.
	"""
	for data in Mem.definitions.values():
		smithed_ignore: JsonDict = data.components.setdefault("custom_data", {}).setdefault("smithed", {}).setdefault("ignore", {})
		smithed_ignore.setdefault("functionality", True)
		smithed_ignore.setdefault("crafting", True)

# Set manual components
def set_manual_components(white_list: list[str]) -> None:
	""" Override the components to include in the manual when hovering items.

	Args:
		white_list: The list of components to include.
	"""
	if not white_list:
		return

	# v2 plugin (ingame_manual): record an override picked up by ManualConfig.from_meta,
	# and update any Manual already created during setup.
	from ...plugins.ingame_manual import config as v2_config
	v2_config.COMPONENTS_OVERRIDE = list(white_list)
	from ...core.__memory__ import Mem
	if Mem.manual is not None:
		Mem.manual.config.components_to_include = list(white_list)

# Export all definitions to JSON
def export_all_definitions_to_json(file_name: str, is_external: bool | JsonDict = False, verbose: bool = True) -> None:
	""" Export all definitions to a single json file for debugging purposes.

	Args:
		file_name:   The name of the file to export to.
		is_external: Whether to export external definitions or not.
					If a JsonDict is provided, it is the source of definitions instead of Mem.definitions or Mem.external_definitions.
		verbose:     Whether to print a debug message or not.
	"""
	# Convert everything to fully serializable dicts
	definitions_copy: dict[str, JsonDict] = {}
	defs = is_external if isinstance(is_external, dict) else (Mem.external_definitions if is_external else Mem.definitions)
	for item, data in defs.items():
		definitions_copy[item] = stp.convert_to_serializable(data)

		# Create a copy of the definitions without OVERRIDE_MODEL key
		if "override_model" in definitions_copy[item]:
			del definitions_copy[item]["override_model"]

	# Export definitions to JSON for debugging generation
	stp.json_dump(definitions_copy, file_name, max_level=3)
	if verbose:
		stp.debug(f"Mem.definitions exported to '{stp.relative_path(file_name)}'")

