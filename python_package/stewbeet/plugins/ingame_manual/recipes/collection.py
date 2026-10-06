"""Craft collection and pure recipe helpers.

``collect_for_item`` gathers an item's own recipes, the crafts that consume it, and mining pseudo-recipes from no-silk-touch drops.
``remove_unknown_crafts`` keeps only craft types that have a registered :class:`~.registry.CraftRenderer`,
so it auto-extends with new types.
"""

# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import math
from collections import Counter
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
from .registry import load_builtin_renderers

if TYPE_CHECKING:
	from .renderer import RecipeRenderer

FURNACE_TYPES = (SmeltingRecipe.type, BlastingRecipe.type, CampfireCookingRecipe.type, SmokingRecipe.type)


@stp.simple_cache(method="str")
def convert_shapeless_to_shaped(craft: JsonDict) -> JsonDict:
	""" Convert a shapeless craft to a readable shaped layout.

	>>> craft = {"type": "crafting_shapeless", "result_count": 1, "ingredients": [{"item": "minecraft:stick"}] * 4}
	>>> shaped = convert_shapeless_to_shaped(craft)
	>>> shaped["type"], shaped["shape"]
	('crafting_shaped', ['AA', 'AA'])
	>>> nine = {
	...     "type": "crafting_shapeless", "result_count": 1,
	...     "ingredients": [{"item": "minecraft:iron_ingot"}] * 8 + [{"item": "minecraft:diamond"}],
	... }
	>>> convert_shapeless_to_shaped(nine)["shape"]
	['AAA', 'ABA', 'AAA']
	"""
	shaped_recipe: JsonDict = {"type": "crafting_shaped", "result_count": craft["result_count"], "ingredients": {}}
	if craft.get("result"):
		shaped_recipe["result"] = craft["result"]

	# One letter per distinct ingredient, in order of first appearance
	key_of: dict[str, str] = {}
	ordered_keys: list[str] = []
	for ingr in craft["ingredients"]:
		key: str = key_of.setdefault(str(ingr), chr(ord("A") + len(key_of)))
		shaped_recipe["ingredients"].setdefault(key, ingr)
		ordered_keys.append(key)
	shaped_recipe["shape"] = shaped_layout(ordered_keys)
	return shaped_recipe


def shaped_layout(ordered_keys: list[str]) -> list[str]:
	""" The grid showing a shapeless craft's ingredients, a ring around the odd one out when there is one.

	>>> shaped_layout(list("AAAAB")), shaped_layout(list("ABBBBCCCC")), shaped_layout(list("ABCDE"))
	([' A ', 'ABA', ' A '], ['BCB', 'CAC', 'BCB'], ['ABC', 'DE'])
	"""
	counts: Counter[str] = Counter(ordered_keys)
	total_items: int = len(ordered_keys)
	if len(counts) == 2 and total_items in (5, 9):
		big: str = "A" if counts["A"] > 1 else "B"
		other: str = "B" if big == "A" else "A"
		if total_items == 9:
			return [big * 3, big + other + big, big * 3]
		return [f" {big} ", big + other + big, f" {big} "]
	if len(counts) == 3 and total_items == 9 and all(count in (1, 4) for count in counts.values()):
		# Counted 1, 4 and 4: the single one sits in the middle
		small: str = min("ABC", key=counts.__getitem__)
		other_1, other_2 = (key for key in "ABC" if key != small)
		return [other_1 + other_2 + other_1, other_2 + small + other_2, other_1 + other_2 + other_1]
	col_size: int = column_count(total_items)
	return ["".join(ordered_keys[i:i + col_size]) for i in range(0, len(ordered_keys), col_size)]


def column_count(total_items: int) -> int:
	""" The columns a grid of `total_items` takes: a square when the count is one, else the narrowest of 2, 3 or 4 that fits.

	>>> [column_count(n) for n in (1, 3, 4, 7, 9, 12, 16)]
	[1, 2, 2, 3, 3, 4, 4]
	"""
	sqrt_items: int = int(math.sqrt(total_items))
	if sqrt_items * sqrt_items == total_items:
		return sqrt_items
	if total_items <= 4:
		return 2
	return 3 if total_items <= 9 else 4


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
	return [c for c in crafts if c["type"] in load_builtin_renderers()]


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


def generate_otherside_crafts(
	item: str, definitions: dict[str, Item], index: dict[str, list[tuple[str, JsonDict]]] | None = None
) -> list[JsonDict]:
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
	# Consumer index cached on the renderer (one instance per manual build,
	# so watch rebuilds and later definition changes get a fresh index).
	cached: tuple[dict[str, Item], dict[str, list[tuple[str, JsonDict]]]] | None = r.consumer_index_cache
	if cached is None or cached[0] is not definitions_as_objects:
		cached = (definitions_as_objects, build_consumer_index(definitions_as_objects))
		r.consumer_index_cache = cached

	crafts: list[JsonDict] = list(item_obj.to_dict().get("recipes", []))
	crafts += generate_otherside_crafts(name, definitions_as_objects, cached[1])
	crafts = remove_duplicate_furnace_crafts(crafts, name)
	crafts = remove_unknown_crafts(crafts)
	crafts = stp.unique_list(crafts)

	ns: str = r.config.project_id
	for ore_name in ores_dropping(name):
		mining_recipe: JsonDict = {"type": "mining", "ingredient": Ingr(ore_name, ns), "result": Ingr(name, ns)}
		add_mining_count(mining_recipe, Mem.definitions[ore_name][NO_SILK_TOUCH_DROP])
		crafts.insert(0, mining_recipe)
	if item_obj.get(NO_SILK_TOUCH_DROP):
		crafts.insert(0, own_mining_recipe(name, item_obj[NO_SILK_TOUCH_DROP], ns))
	return crafts


def ores_dropping(name: str) -> list[str]:
	""" The items that drop `name` when mined without silk touch. """
	return [i for i, d in Mem.definitions.items() if d.get(NO_SILK_TOUCH_DROP) and drop_id(d[NO_SILK_TOUCH_DROP]) == name]


def drop_id(drop: JsonDict | NoSilkTouchDrop | str | LootTable) -> str | None:
	""" The item a no silk touch drop gives, None for a loot table. """
	if isinstance(drop, str):
		return drop
	return drop["id"] if isinstance(drop, dict | NoSilkTouchDrop) else None


def own_mining_recipe(name: str, drop: JsonDict | NoSilkTouchDrop | str | LootTable, ns: str) -> JsonDict:
	""" The pseudo recipe showing what mining `name` without silk touch drops, a loot table's drop being dynamic. """
	mining_recipe: JsonDict
	if isinstance(drop, LootTable):
		mining_recipe = {"type": "mining", "ingredient": Ingr(name, ns), "dynamic_drop": True}
	else:
		result_format: str = drop if isinstance(drop, str) else drop["id"]
		mining_recipe = {"type": "mining", "ingredient": Ingr(name, ns), "result": Ingr(result_format, ns)}
	add_mining_count(mining_recipe, drop)
	return mining_recipe


def add_mining_count(mining_recipe: JsonDict, drop: JsonDict | NoSilkTouchDrop | str | LootTable) -> None:
	""" Mark a loot table's drop as dynamic, or show the count a drop gives, `min-max` for a range.

	>>> recipe = {}
	>>> add_mining_count(recipe, {"id": "x", "count": {"min": 1, "max": 3}}); recipe
	{'result_count': '1-3'}
	"""
	if isinstance(drop, LootTable):
		mining_recipe["dynamic_drop"] = True
		return
	if not isinstance(drop, dict | NoSilkTouchDrop) or "count" not in drop:
		return
	count_data: JsonDict | int = drop["count"]
	if not isinstance(count_data, dict):
		mining_recipe["result_count"] = str(count_data)
	elif "min" in count_data and "max" in count_data:
		mining_recipe["result_count"] = f"{count_data['min']}-{count_data['max']}"
	elif "min" in count_data:
		mining_recipe["result_count"] = str(count_data["min"])
	elif "max" in count_data:
		mining_recipe["result_count"] = str(count_data["max"])

