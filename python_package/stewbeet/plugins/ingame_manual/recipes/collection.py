"""Craft collection + pure recipe helpers (ported from v1 ``other_utils``).

``collect_for_item`` gathers an item's own recipes, the crafts that consume it, and mining
pseudo-recipes from no-silk-touch drops. ``remove_unknown_crafts`` keeps only craft types that
have a registered :class:`~.registry.CraftRenderer`, so it auto-extends with new types.
"""

# Imports
from __future__ import annotations

import math
from typing import TYPE_CHECKING, cast

import stouputils as stp
from beet import LootTable
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import NoSilkTouchDrop
from ....core.cls.ingredients import Ingr
from ....core.cls.item import Item
from ....core.cls.recipe import BlastingRecipe, CampfireCookingRecipe, RecipeBase, SmeltingRecipe, SmokingRecipe
from ....core.constants import NO_SILK_TOUCH_DROP
from .registry import CRAFT_RENDERERS

if TYPE_CHECKING:
	from .renderer import RecipeRenderer

FURNACE_TYPES = (SmeltingRecipe.type, BlastingRecipe.type, CampfireCookingRecipe.type, SmokingRecipe.type)


@stp.simple_cache
def convert_shapeless_to_shaped(craft: JsonDict) -> JsonDict:
	""" Convert a shapeless craft to a readable shaped layout.

	>>> craft = {"type": "crafting_shapeless", "result_count": 1, "ingredients": [{"item": "minecraft:stick"}] * 4}
	>>> shaped = convert_shapeless_to_shaped(craft)
	>>> shaped["type"], shaped["shape"]
	('crafting_shaped', ['AA', 'AA'])
	>>> nine = {"type": "crafting_shapeless", "result_count": 1, "ingredients": [{"item": "minecraft:iron_ingot"}] * 8 + [{"item": "minecraft:diamond"}]}
	>>> convert_shapeless_to_shaped(nine)["shape"]
	['AAA', 'ABA', 'AAA']
	"""
	shapeless_ingredients: list[str] = craft["ingredients"]
	total_items: int = len(shapeless_ingredients)
	shaped_recipe: JsonDict = {"type": "crafting_shaped", "result_count": craft["result_count"], "ingredients": {}}
	if craft.get("result"):
		shaped_recipe["result"] = craft["result"]

	next_key: str = "A"
	ingredient_to_key: dict[str, str] = {}
	ingredient_counts: dict[str, int] = {}
	ordered_keys: list[str] = []
	for ingr in shapeless_ingredients:
		ingr_str = str(ingr)
		if ingr_str not in ingredient_to_key:
			ingredient_to_key[ingr_str] = next_key
			shaped_recipe["ingredients"][next_key] = ingr
			next_key = chr(ord(next_key) + 1)
		ingredient_counts[ingr_str] = ingredient_counts.get(ingr_str, 0) + 1
		ordered_keys.append(ingredient_to_key[ingr_str])

	if len(shaped_recipe["ingredients"]) == 2 and total_items in (5, 9):
		len_same: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["A"])])
		big: str = "A" if len_same > 1 else "B"
		other: str = "B" if big == "A" else "A"
		if total_items == 9:
			shaped_recipe["shape"] = [big * 3, big + other + big, big * 3]
		elif total_items == 5:
			shaped_recipe["shape"] = [f" {big} ", big + other + big, f" {big} "]
	elif len(shaped_recipe["ingredients"]) == 3 and total_items == 9 and all(count in (1, 4) for count in ingredient_counts.values()):
		len_A: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["A"])])
		len_B: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["B"])])
		len_C: int = len([x for x in shapeless_ingredients if str(x) == str(shaped_recipe["ingredients"]["C"])])
		small: str = "A" if len_A < len_B and len_A < len_C else "B" if len_B < len_C else "C"
		other_1: str = "B" if small == "A" else "A" if small == "C" else "C"
		other_2: str = "C" if small == "A" else "C" if small == "B" else "B"
		shaped_recipe["shape"] = [other_1 + other_2 + other_1, other_2 + small + other_2, other_1 + other_2 + other_1]
	else:
		sqrt_items = int(math.sqrt(total_items))
		if sqrt_items * sqrt_items == total_items:
			col_size = sqrt_items
		elif total_items <= 4:
			col_size = 2
		elif total_items <= 9:
			col_size = 3
		else:
			col_size = 4
		shaped_recipe["shape"] = ["".join(ordered_keys[i:i + col_size]) for i in range(0, len(ordered_keys), col_size)]
	return shaped_recipe


def remove_duplicate_furnace_crafts(crafts: list[JsonDict], item: str) -> list[JsonDict]:
	""" Keep only one furnace craft per (ingredient, result, count) triple. """
	seen_pairs: set[tuple[str, str, int]] = set()
	unique_crafts: list[JsonDict] = []
	for craft in crafts:
		if craft["type"] in FURNACE_TYPES:
			ingredient_id = Ingr(craft["ingredient"]).to_id(add_namespace=True)
			result_id = Ingr(craft["result"]).to_id(add_namespace=True) if "result" in craft else item
			pair = (ingredient_id, result_id, craft.get("result_count", 1))
			if pair not in seen_pairs:
				seen_pairs.add(pair)
				unique_crafts.append(craft)
		else:
			unique_crafts.append(craft)
	return unique_crafts


def remove_unknown_crafts(crafts: list[JsonDict]) -> list[JsonDict]:
	""" Drop crafts whose type has no registered renderer. """
	return [c for c in crafts if c["type"] in CRAFT_RENDERERS]


def craft_ingredient_ids(craft: RecipeBase) -> set[str]:
	""" All ingredient ids (without namespace) appearing in a craft. """
	ids: set[str] = set()
	if craft.get("ingredient"):
		ids.add(Ingr(craft["ingredient"]).to_id(add_namespace=False))
	ingredients: JsonDict | list[JsonDict] | None = craft.get("ingredients")
	if isinstance(ingredients, dict):
		ids.update(Ingr(x).to_id(add_namespace=False) for x in ingredients.values())
	elif isinstance(ingredients, list):
		ids.update(Ingr(x).to_id(add_namespace=False) for x in ingredients)
	return ids


def item_in_ingredients(item: str, craft: RecipeBase) -> bool:
	""" Whether ``item`` appears among a craft's ingredients. """
	return item in craft_ingredient_ids(craft)


def build_consumer_index(definitions: dict[str, Item]) -> dict[str, list[tuple[str, JsonDict]]]:
	""" Map each ingredient id to the (consumer item, craft) pairs that consume it.

	One pass over all recipes, so :func:`generate_otherside_crafts` becomes a dict lookup
	instead of an O(items x recipes) rescan per item.
	"""
	index: dict[str, list[tuple[str, JsonDict]]] = {}
	for other, obj in definitions.items():
		for craft in obj.recipes:
			for ingr_id in craft_ingredient_ids(craft):
				index.setdefault(ingr_id, []).append((other, cast(JsonDict, craft)))
	return index


def generate_otherside_crafts(item: str, definitions: dict[str, Item], index: dict[str, list[tuple[str, JsonDict]]] | None = None) -> list[JsonDict]:
	""" Find crafts in other items that consume ``item`` (the "used for crafting" list). """
	if index is None:
		index = build_consumer_index(definitions)
	crafts: list[JsonDict] = []
	for other, craft in index.get(item, []):
		if other != item:
			craft_copy: JsonDict = craft.copy()
			craft_copy["result"] = Ingr(other, count=craft["result_count"]) if "result" not in craft else craft["result"]
			crafts.append(craft_copy)
	return crafts


def collect_for_item(r: RecipeRenderer, name: str, item_obj: Item, definitions_as_objects: dict[str, Item]) -> list[JsonDict]:
	""" Gather an item's own recipes, otherside crafts, and mining drops (deduped). """
	# Consumer index cached on the renderer (one instance per manual build, so watch
	# rebuilds and later definition changes get a fresh index).
	cached: tuple[dict[str, Item], dict[str, list[tuple[str, JsonDict]]]] | None = r.consumer_index_cache
	if cached is None or cached[0] is not definitions_as_objects:
		cached = (definitions_as_objects, build_consumer_index(definitions_as_objects))
		r.consumer_index_cache = cached

	crafts: list[JsonDict] = list(item_obj.to_dict().get("recipes", []))
	crafts += generate_otherside_crafts(name, definitions_as_objects, cached[1])
	crafts = remove_duplicate_furnace_crafts(crafts, name)
	crafts = remove_unknown_crafts(crafts)
	crafts = stp.unique_list(crafts)

	def add_count_to_mining_recipe(mining_recipe: JsonDict, no_silk_drop_data: JsonDict | NoSilkTouchDrop | str | LootTable) -> None:
		if isinstance(no_silk_drop_data, LootTable):
			mining_recipe["dynamic_drop"] = True
			return
		if isinstance(no_silk_drop_data, dict | NoSilkTouchDrop) and "count" in no_silk_drop_data:
			count_data: JsonDict | int = no_silk_drop_data["count"]
			if isinstance(count_data, dict):
				if "min" in count_data and "max" in count_data:
					mining_recipe["result_count"] = f"{count_data['min']}-{count_data['max']}"
				elif "min" in count_data:
					mining_recipe["result_count"] = str(count_data["min"])
				elif "max" in count_data:
					mining_recipe["result_count"] = str(count_data["max"])
			else:
				mining_recipe["result_count"] = str(count_data)

	ns = r.config.project_id
	# Items that this item is the no-silk drop of (this item is the result of mining an ore)
	is_drop_of: list[str] = [
		i for i, d in Mem.definitions.items()
		if d.get(NO_SILK_TOUCH_DROP) and (
			(isinstance(d[NO_SILK_TOUCH_DROP], str) and d[NO_SILK_TOUCH_DROP] == name) or
			(isinstance(d[NO_SILK_TOUCH_DROP], dict | NoSilkTouchDrop) and d[NO_SILK_TOUCH_DROP]["id"] == name)
		)
	]
	for ore_name in is_drop_of:
		mining_recipe: JsonDict = {"type": "mining", "ingredient": Ingr(ore_name, ns), "result": Ingr(name, ns)}
		add_count_to_mining_recipe(mining_recipe, Mem.definitions[ore_name][NO_SILK_TOUCH_DROP])
		crafts.insert(0, mining_recipe)

	# This item is an ore with its own no-silk drop
	if item_obj.get(NO_SILK_TOUCH_DROP):
		data = item_obj[NO_SILK_TOUCH_DROP]
		if isinstance(data, LootTable):
			mining_recipe = {"type": "mining", "ingredient": Ingr(name, ns), "dynamic_drop": True}
		else:
			result_format: str = data if isinstance(data, str) else data["id"]
			mining_recipe = {"type": "mining", "ingredient": Ingr(name, ns), "result": Ingr(result_format, ns)}
		add_count_to_mining_recipe(mining_recipe, data)
		crafts.insert(0, mining_recipe)

	return crafts

