
# pyright: reportUnknownMemberType=false
# ruff: noqa: E501
# Imports
from typing import Any, cast

import stouputils as stp
from beet import Context
from beet.core.utils import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.block import VANILLA_BLOCK_FOR_ORES, VanillaBlock
from ...core.cls.ingredients import FURNACES_RECIPES_TYPES
from ...core.cls.item import Item
from ...core.constants import (
	CATEGORY,
	CUSTOM_BLOCK_ALTERNATIVE,
	CUSTOM_BLOCK_VANILLA,
	GROWING_SEED,
	NO_SILK_TOUCH_DROP,
	PAINTING_DATA,
	RESULT_OF_CRAFTING,
	USED_FOR_CRAFTING,
	VANILLA_BLOCK,
)


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.verify_definitions'")
def beet_default(ctx: Context) -> None:
	""" Database verification plugin for StewBeet.
	Verifies the definitions structure, validates item configurations, and performs consistency checks.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# Get configuration data from context
	stewbeet_config: JsonDict = ctx.meta.get("stewbeet", {})
	definitions_debug: str = stewbeet_config.get("definitions_debug", "")

	# Create a copy of the definitions without OVERRIDE_MODEL key
	definitions_copy: dict[str, JsonDict] = {}
	for item, data in Mem.definitions.items():
		# Convert Item objects or dicts with nested Recipe objects to fully serializable dicts
		definitions_copy[item] = stp.convert_to_serializable(data)
		if "override_model" in definitions_copy[item]:
			del definitions_copy[item]["override_model"]

	# Export definitions to JSON for debugging generation
	if definitions_debug and definitions_copy:
		stp.json_dump(definitions_copy, definitions_debug, max_level=3)
		stp.debug(f"Received definitions exported to './{stp.relative_path(definitions_debug)}'")

	# Check every single thing in the definitions
	errors: list[str] = []
	warnings: list[str] = []
	for item, data in Mem.definitions.items():
		if isinstance(data, Item):
			continue	# Already checked

		# Check if components doesn't start with "minecraft:", if so rename them
		to_replace: bool = False
		for k in data.keys():
			if k.startswith("minecraft:"):
				warnings.append(f"Remove the 'minecraft:' prefix from key '{k}' in item '{item}', as it's automatically added by stewbeet.")
				to_replace = True
		if to_replace:
			Mem.definitions[item] = data = {k.replace("minecraft:", "", 1) if k.startswith("minecraft:") else k: v for k, v in data.items()}

		# Check if the item uses a reserved name
		if item == "heavy_workbench":
			errors.append(f"'{item}' is reserved for the heavy workbench used for NBT recipes, please use another name")

		# Check for a proper ID
		if not data.get("id"):
			errors.append(f"'id' key missing for '{item}'")
		else:
			if not isinstance(data["id"], str):
				errors.append(f"'id' key should be a string for '{item}'")
			elif ":" not in data["id"]:
				errors.append(f"'id' key should be namespaced in the format 'minecraft:{data['id']}' for '{item}'")
			elif data["id"] == VANILLA_BLOCK_FOR_ORES["id"]:
				errors.append(f"'id' key should not be '{VANILLA_BLOCK_FOR_ORES['id']}' for '{item}', it's a reserved ID")

			# Force VANILLA_BLOCK key for custom blocks
			elif data["id"] in [CUSTOM_BLOCK_VANILLA, CUSTOM_BLOCK_ALTERNATIVE]:
				if not data.get(VANILLA_BLOCK):
					errors.append(f"VANILLA_BLOCK key missing for '{item}', needed format: VANILLA_BLOCK: {{\"id\":\"minecraft:stone\", \"apply_facing\":False}}.")
				elif isinstance(data[VANILLA_BLOCK], VanillaBlock):
					pass
				elif not isinstance(data[VANILLA_BLOCK], dict):
					errors.append(f"VANILLA_BLOCK key should be a dictionary for '{item}', found '{data[VANILLA_BLOCK]}', needed format: VANILLA_BLOCK: {{\"id\":\"minecraft:stone\", \"apply_facing\":False}}.")
				elif (data[VANILLA_BLOCK].get("id", None) is None) and (data[VANILLA_BLOCK].get("contents", None) is not True):
					errors.append(f"VANILLA_BLOCK key should have an 'id' key for '{item}', found '{data[VANILLA_BLOCK]}', needed format: VANILLA_BLOCK: {{\"id\":\"minecraft:stone\", \"apply_facing\":False}}.")
				elif (data[VANILLA_BLOCK].get("apply_facing", None) is None) and (data[VANILLA_BLOCK].get("contents", None) is not True):
					errors.append(f"VANILLA_BLOCK key should have a 'apply_facing' key to boolean for '{item}', found '{data[VANILLA_BLOCK]}', needed format: VANILLA_BLOCK: {{\"id\":\"minecraft:stone\", \"apply_facing\":False}}.")

			# Prevent the use of "container" key for custom blocks
			elif data["id"] == CUSTOM_BLOCK_VANILLA and data.get("container"):
				errors.append(f"'container' key should not be used for '{item}', it's a reserved key for custom blocks, prefer writing to the place function to fill in the container")

		# If a category is present but wrong format, log an error
		if data.get(CATEGORY) and not isinstance(data[CATEGORY], str):
			errors.append(f"CATEGORY key should be a string for '{item}'")

		# Check for a proper custom data
		if data.get("custom_data") and not isinstance(data["custom_data"], dict):
			errors.append(f"'custom_data' key should be a dictionary for '{item}'")
		elif not data.get("custom_data") or not data["custom_data"].get(ctx.project_id) or not isinstance(data["custom_data"][ctx.project_id], dict) or not data["custom_data"][ctx.project_id].get(item) or not isinstance(data["custom_data"][ctx.project_id][item], bool):
			errors.append(f"'custom_data' key missing proper data for '{item}', should have at least \"custom_data\": {{ctx.project_id: {{\"{item}\": True}}}}")

		# Check for wrong custom ores data
		if data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES and not data.get(NO_SILK_TOUCH_DROP):
			errors.append(f"NO_SILK_TOUCH_DROP key missing for '{item}', should be the ID of the block that drops when mined without silk touch")
		if data.get(NO_SILK_TOUCH_DROP):
			no_silk_drop = data[NO_SILK_TOUCH_DROP]
			if isinstance(no_silk_drop, str):
				# Old format: just a string item ID (can be "item_name" or "minecraft:stone")
				pass
			elif isinstance(no_silk_drop, dict):
				# New format: {"id": "item_id", "count": 5} or {"id": "item_id", "count": {"min": 1, "max": 4}}
				no_silk_drop = cast(JsonDict, no_silk_drop)
				if not no_silk_drop.get("id") or not isinstance(no_silk_drop["id"], str):
					errors.append(f"NO_SILK_TOUCH_DROP key should have a string 'id' field for '{item}', ex: {{\"id\": \"stardust_fragment\", \"count\": {{\"min\": 1, \"max\": 4}}}} or {{\"id\": \"minecraft:stone\", \"count\": 1}}")
				if no_silk_drop.get("count"):
					count = no_silk_drop["count"]
					if isinstance(count, int):
						# Single integer count is valid
						pass
					elif isinstance(count, dict):
						# Dictionary with min and max keys
						count_dict = cast(JsonDict, count)
						if not count_dict.get("min") or not isinstance(count_dict["min"], int):
							errors.append(f"NO_SILK_TOUCH_DROP 'count' dict should have an integer 'min' field for '{item}', ex: {{\"min\": 1, \"max\": 4}}")
						if not count_dict.get("max") or not isinstance(count_dict["max"], int):
							errors.append(f"NO_SILK_TOUCH_DROP 'count' dict should have an integer 'max' field for '{item}', ex: {{\"min\": 1, \"max\": 4}}")
					else:
						errors.append(f"NO_SILK_TOUCH_DROP 'count' field should be an integer or dict with min/max keys for '{item}', ex: 1 or {{\"min\": 1, \"max\": 4}}")
			else:
				errors.append(f"NO_SILK_TOUCH_DROP key should be a string or dict for '{item}', ex: \"adamantium_fragment\", \"minecraft:stone\", or {{\"id\": \"stardust_fragment\", \"count\": {{\"min\": 1, \"max\": 4}}}}")

		# Force the use of "item_name" key for every item
		if not data.get("item_name"):
			errors.append(f"'item_name' key missing for '{item}', should be a Text Component, ex: {{\"text\":\"This is an Item Name\"}} or [\"This is an Item Name\"]")
		elif not isinstance(data["item_name"], dict | list | str):
			errors.append(f"'item_name' key should be a Text Component for '{item}', got '{data['item_name']}'")

		# Force the use of "lore" key to be in a correct format
		if data.get("lore"):
			if not isinstance(data["lore"], list):
				errors.append(f"'lore' key should be a list for '{item}', got {data['lore']}")
			else:
				lore = cast(list[JsonDict | None], data["lore"])
				for i, line in enumerate(lore):
					if not isinstance(line, dict | list | str):
						errors.append(f"Line #{i} in 'lore' key should be a Text Component for '{item}', ex: {{\"text\":\"This is a lore line\"}} or [\"This is a lore line\"]")

		# Check all the recipes
		if RESULT_OF_CRAFTING in data or USED_FOR_CRAFTING in data:

			# Get a list of recipes
			crafts_to_check: list[Any] = [*data.get(RESULT_OF_CRAFTING, []), *data.get(USED_FOR_CRAFTING, [])]

			# Check each recipe
			for i, r in enumerate(crafts_to_check):

				# A recipe is always a dictionnary
				if not isinstance(r, dict):
					errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should be a dictionary for '{item}'")
				else:
					recipe = cast(JsonDict, r)

					# Verify "type" key
					if not recipe.get("type") or not isinstance(recipe["type"], str):
						errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a string 'type' key for '{item}'")
					else:

						# Check the crafting_shaped type
						if recipe["type"] == "crafting_shaped":
							if not recipe.get("shape") or not isinstance(recipe["shape"], list):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a list[str] 'shape' key for '{item}'")
							elif len(recipe["shape"]) > 3 or len(recipe["shape"][0]) > 3: # pyright: ignore[reportUnknownArgumentType]
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a maximum of 3 rows and 3 columns for '{item}'")
							else:
								shape = cast(list[str], recipe["shape"])
								row_size = len(shape[0])
								if any(len(row) != row_size for row in shape):
									errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have the same number of columns for each row for '{item}'")

							if not recipe.get("ingredients") or not isinstance(recipe["ingredients"], dict):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict 'ingredients' key for '{item}'")
							else:
								ingredients = cast(JsonDict, recipe["ingredients"])
								for symbol, ingredient in ingredients.items():
									if not isinstance(ingredient, dict):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict ingredient for symbol '{symbol}' for '{item}'")
									elif not ingredient.get("item") and not ingredient.get("components"):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have an 'item' or 'components' key for ingredient of symbol '{symbol}' for '{item}', please use 'ingr_repr' function")
									elif ingredient.get("components") and not isinstance(ingredient["components"], dict):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict 'components' key for ingredient of symbol '{symbol}' for '{item}', please use 'ingr_repr' function")
									shape = cast(list[str], recipe["shape"])
									if not any(symbol in line for line in shape):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a symbol '{symbol}' in the shape for '{item}'")

						# Check the crafting_shapeless type
						elif recipe["type"] == "crafting_shapeless":
							if not recipe.get("ingredients") or not isinstance(recipe["ingredients"], list):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a list 'ingredients' key for '{item}'")
							else:
								ingredients = cast(list[Any], recipe["ingredients"])
								for ingredient in ingredients:
									if not isinstance(ingredient, dict):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict ingredient for '{item}'")
									elif not ingredient.get("item") and not ingredient.get("components"):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have an 'item' or 'components' key for ingredient for '{item}', please use 'ingr_repr' function")
									elif ingredient.get("components") and not isinstance(ingredient["components"], dict):
										errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict 'components' key for ingredient for '{item}', please use 'ingr_repr' function")

						# Check the furnaces recipes
						elif recipe["type"] in FURNACES_RECIPES_TYPES:
							if not recipe.get("ingredient") or not isinstance(recipe["ingredient"], dict):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict 'ingredient' key for '{item}'")
							elif not recipe["ingredient"].get("item") and not recipe["ingredient"].get("components"):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have an 'item' or 'components' key for ingredient for '{item}', please use 'ingr_repr' function")
							elif recipe["ingredient"].get("components") and not isinstance(recipe["ingredient"]["components"], dict):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a dict 'components' key for ingredient for '{item}', please use 'ingr_repr' function")

							if not recipe.get("experience") or not isinstance(recipe["experience"], float | int):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have a float 'experience' key for '{item}'")
							if not recipe.get("cookingtime") or not isinstance(recipe["cookingtime"], int):
								errors.append(f"Recipe #{i} in RESULT_OF_CRAFTING should have an int 'cookingtime' key for '{item}'")

		# Check the PAINTING_DATA key
		if data.get(PAINTING_DATA):
			if data["id"] != "minecraft:painting":
				errors.append(f"PAINTING_DATA key should only be used with 'id' equal to 'minecraft:painting' for '{item}', found '{data['id']}' instead")
			elif not isinstance(data[PAINTING_DATA], dict):
				errors.append(f"PAINTING_DATA key should be a dictionary for '{item}'")
			else:
				painting_data = cast(JsonDict, data[PAINTING_DATA])
				if painting_data.get("author") and not isinstance(painting_data["author"], dict | list | str):
					errors.append(f"PAINTING_DATA 'author' key should be a Text Component for '{item}', got '{painting_data['author']}'")
				if painting_data.get("title") and not isinstance(painting_data["title"], dict | list | str):
					errors.append(f"PAINTING_DATA 'title' key should be a Text Component for '{item}', got '{painting_data['title']}'")
				if not painting_data.get("width") or not isinstance(painting_data["width"], int) or painting_data["width"] < 1 or painting_data["width"] > 16:
					errors.append(f"PAINTING_DATA should have an integer 'width' key between 1 and 16 for '{item}'")
				if not painting_data.get("height") or not isinstance(painting_data["height"], int) or painting_data["height"] < 1 or painting_data["height"] > 16:
					errors.append(f"PAINTING_DATA should have an integer 'height' key between 1 and 16 for '{item}'")

				# Add missing data if needed
				if "painting/variant" not in data:
					data["painting/variant"] = f"{ctx.project_id}:{item}"

		# Check the GROWING_SEED key
		if data.get(GROWING_SEED):
			if not isinstance(data[GROWING_SEED], dict):
				errors.append(f"GROWING_SEED key should be a dictionary for '{item}'")
			else:
				growing_seed: JsonDict = data[GROWING_SEED]
				if not growing_seed.get("seconds") or not isinstance(growing_seed["seconds"], int):
					errors.append(f"GROWING_SEED should have an integer 'seconds' key for '{item}'")
				if not growing_seed.get("loots") or not isinstance(growing_seed["loots"], list):
					errors.append(f"GROWING_SEED should have a list 'loots' key for '{item}'")
				else:
					loots = cast(list[Any], growing_seed["loots"])
					for i, loot in enumerate(loots):
						if not isinstance(loot, dict):
							errors.append(f"GROWING_SEED loot #{i} should be a dictionary for '{item}'")
						else:
							loot = cast(JsonDict, loot)
							if not loot.get("id") or not isinstance(loot["id"], str):
								errors.append(f"GROWING_SEED loot #{i} should have a string 'id' key for '{item}'")
							if loot.get("rolls"):
								rolls = loot["rolls"]
								if isinstance(rolls, int):
									pass # Integer is valid
								elif isinstance(rolls, dict):
									rolls_dict = cast(JsonDict, rolls)
									if not rolls_dict.get("type") or not isinstance(rolls_dict["type"], str):
										errors.append(f"GROWING_SEED loot #{i} 'rolls' dict should have a string 'type' key for '{item}', ex: {{\"type\":\"minecraft:uniform\",\"min\":1,\"max\":2}}")
								else:
									errors.append(f"GROWING_SEED loot #{i} 'rolls' should be an integer or dict for '{item}', ex: 1 or {{\"type\":\"minecraft:uniform\",\"min\":1,\"max\":2}}")
							else:
								loot["rolls"] = 1 # Default rolls to 1 if not present

							# Check fortune key (optional)
							if loot.get("fortune"):
								fortune = loot["fortune"]
								if not isinstance(fortune, dict):
									errors.append(f"GROWING_SEED loot #{i} 'fortune' should be a dictionary for '{item}'")
								else:
									fortune_dict = cast(JsonDict, fortune)
									if (not fortune_dict.get("extra") and fortune_dict.get("extra") != 0) or not isinstance(fortune_dict.get("extra"), int | float):
										errors.append(f"GROWING_SEED loot #{i} 'fortune' dict should have a numeric 'extra' key for '{item}', ex: {{\"extra\":0,\"probability\":0.1}}")
									if (not fortune_dict.get("probability") and fortune_dict.get("probability") != 0) or not isinstance(fortune_dict.get("probability"), float | int):
										errors.append(f"GROWING_SEED loot #{i} 'fortune' dict should have a numeric 'probability' key for '{item}', ex: {{\"extra\":0,\"probability\":0.1}}")
				if growing_seed.get("texture_basename") and not isinstance(growing_seed["texture_basename"], str):
					errors.append(f"GROWING_SEED 'texture_basename' key should be a string for '{item}'")
				elif not growing_seed.get("texture_basename"):
					growing_seed["texture_basename"] = item
				if growing_seed.get("planted_on"):
					if not isinstance(growing_seed["planted_on"], str):
						errors.append(f"GROWING_SEED 'planted_on' key should be a string for '{item}'")
					elif "minecraft:" in growing_seed["planted_on"]:
						warnings.append(f"Remove the 'minecraft:' prefix from 'planted_on' in GROWING_SEED for '{item}', as it's automatically added by stewbeet.")
						data[GROWING_SEED]["planted_on"] = growing_seed["planted_on"].replace("minecraft:", "")
				else:
					growing_seed["planted_on"] = "dirt" # Default to dirt if not present

	# Log errors if any
	if errors:
		stp.error("Errors found in the definitions during verification:\n- " + "\n- ".join(errors))
	elif warnings:
		stp.warning("Warnings found in the definitions during verification:\n- " + "\n- ".join(warnings))
	else:
		stp.info("No errors found in the definitions during verification")

	# Final adjustments to the definitions
	for item, data in Mem.definitions.items():
		if isinstance(data, Item):
			continue	# Already done

		# Add default group to every recipe
		for recipe in [*data.get(RESULT_OF_CRAFTING, []), *data.get(USED_FOR_CRAFTING, [])]:
			recipe.setdefault("group", item)

		# Add additional data to the custom blocks
		if data.get("id") == CUSTOM_BLOCK_VANILLA:
			data["container"] = [
				{"slot":0,"item":{"id":"minecraft:stone","count":1,"components":{"minecraft:custom_data":{"smithed":{"block":{"id":f"{ctx.project_id}:{item}","from":ctx.project_id}}}}}}
			]

			# Hide the container tooltip
			if not data.get("tooltip_display"):
				data["tooltip_display"] = {"hidden_components": []}
			elif not data["tooltip_display"].get("hidden_components"):
				data["tooltip_display"]["hidden_components"] = []
			hidden_components: list[str] = data["tooltip_display"]["hidden_components"] # type: ignore
			hidden_components.append("minecraft:container")
			data["tooltip_display"]["hidden_components"] = stp.unique_list(hidden_components)

		# Add additional data to the custom blocks alternative
		elif data.get("id") == CUSTOM_BLOCK_ALTERNATIVE:
			data["entity_data"] = {"id":"minecraft:item_frame","Tags":[f"{ctx.project_id}.new",f"{ctx.project_id}.{item}"],"Invisible":True,"Silent":True}
			pass

		# Fix !component values
		for k, v in data.items():
			if k.startswith("!") and v != {}:
				data[k] = {}

