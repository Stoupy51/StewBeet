
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import Any

import stouputils as stp
from stouputils.typing import JsonDict

from .versions import minecraft_version_at_least

# Constants
TYPED_LOOT_VERSION: tuple[int, int] = (26, 3)
""" First Minecraft version dispatching loot functions and conditions on "type", with single "condition" and "modifier" fields. """


# Utility function to convert result_count to string suffix
@stp.simple_cache(method="str")
def result_count_to_suffix(result_count: int | JsonDict) -> str:
	""" Convert a result count to a string suffix for loot table paths

	Args:
		result_count (int | JsonDict): The count of the result item, can be an int or a dict for random counts
			ex: 1
			ex: {"type": "minecraft:uniform","min": 4,"max": 6}
	Returns:
		str: The suffix string, ex: "" or "_x5" or "_x4to6"

	Examples:
		>>> result_count_to_suffix(1)
		''
		>>> result_count_to_suffix(5)
		'_x5'
		>>> result_count_to_suffix({"min": 4, "max": 6})
		'_x4to6'
		>>> result_count_to_suffix({"min": 3, "max": 1})
		'_x3'
		>>> result_count_to_suffix({"min": 1, "max": 1})
		''
		>>> result_count_to_suffix({})
		''
	"""
	if isinstance(result_count, int):
		if result_count > 1:
			return f"_x{result_count}"
		return ""
	elif hasattr(result_count, "get"):
		minimum = result_count.get("min", 1)
		maximum = result_count.get("max", 1)
		if maximum > 1:
			return f"_x{minimum}to{maximum}"
		elif minimum > 1:
			return f"_x{minimum}"
	return ""


# Version-aware loot formats
def loot_function(function: str, **fields: Any) -> JsonDict:
	""" Loot function (item modifier) keyed the way the targeted Minecraft version reads it.

	>>> loot_function("minecraft:set_count", count=2)
	{'type': 'minecraft:set_count', 'count': 2}
	"""
	return {"type" if minecraft_version_at_least(TYPED_LOOT_VERSION) else "function": function, **fields}


def loot_condition(condition: str, **fields: Any) -> JsonDict:
	""" Loot condition (predicate) keyed the way the targeted Minecraft version reads it.

	>>> loot_condition("minecraft:random_chance", chance=0.5)
	{'type': 'minecraft:random_chance', 'chance': 0.5}
	"""
	return {"type" if minecraft_version_at_least(TYPED_LOOT_VERSION) else "condition": condition, **fields}


def loot_modifiers(functions: list[JsonDict]) -> JsonDict:
	""" Field applying loot functions to a pool entry, to unpack into that entry.

	>>> loot_modifiers([loot_function("minecraft:set_count", count=2)])
	{'modifier': [{'type': 'minecraft:set_count', 'count': 2}]}
	"""
	return {"modifier" if minecraft_version_at_least(TYPED_LOOT_VERSION) else "functions": functions}


def float_score(objective: str, target: str = "this") -> JsonDict:
	""" Float number provider reading a score, for fields such as set_custom_model_data floats.

	Since 26.3 only integer providers read scores, so the score is converted with from_int.

	>>> float_score("energy.data")
	{'type': 'minecraft:from_int', 'input': {'type': 'minecraft:score', 'target': 'this', 'score': 'energy.data'}}
	"""
	score: JsonDict = {"type": "minecraft:score", "target": target, "score": objective}
	return {"type": "minecraft:from_int", "input": score} if minecraft_version_at_least(TYPED_LOOT_VERSION) else score


def advancement_conditions(conditions: list[JsonDict]) -> JsonDict | list[JsonDict]:
	""" Value of an advancement trigger field holding conditions, such as "player" or "location".

	A list before 26.3, a single condition since, wrapped in all_of when there are several.

	>>> advancement_conditions([loot_condition("minecraft:random_chance", chance=0.5)])
	{'type': 'minecraft:random_chance', 'chance': 0.5}
	"""
	if not minecraft_version_at_least(TYPED_LOOT_VERSION):
		return conditions
	return conditions[0] if len(conditions) == 1 else loot_condition("minecraft:all_of", terms=conditions)


def advancement_entity(predicate: JsonDict) -> JsonDict:
	""" Value of an advancement trigger field matching an entity, such as "entity" or "player".

	A bare entity predicate before 26.3, an entity_properties condition on it since.

	>>> advancement_entity({"type": "minecraft:pig"})["predicate"]
	{'type': 'minecraft:pig'}
	"""
	if not minecraft_version_at_least(TYPED_LOOT_VERSION):
		return predicate
	return loot_condition("minecraft:entity_properties", entity="this", predicate=predicate)

