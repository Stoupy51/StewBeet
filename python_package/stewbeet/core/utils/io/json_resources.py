""" Writing JSON pack resources by path, merged into whatever another plugin already wrote there. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Callable, MutableMapping

from beet import Advancement, Enchantment, JsonFile, Predicate
from stouputils.typing import JsonDict

from ...__memory__ import Mem
from .dicts import super_merge_dict
from .files import set_json_encoder


# Functions
def write_json_resource[T: JsonFile](
	registry: MutableMapping[str, T],
	file_type: type[T],
	path: str,
	data: T | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True, # pyright: ignore[reportUnknownLambdaType]
) -> T | None:
	""" Write a JSON resource of any registry, merging it into the existing one with super_merge_dict.

	Args:
		registry:  Where it goes (ex: Mem.ctx.data.item_modifiers)
		file_type: Its beet class (ex: ItemModifier)
		path:      Its resource location (ex: "namespace:folder/name"), with or without ".json"
		overwrite: Replace the existing resource instead of merging into it
		max_level: Maximum depth of the JSON dump, -1 for the default
		condition: Receives the existing data and decides whether to write at all
	Returns:
		The written resource, or None when the condition refused it
	"""
	path = path.removesuffix(".json")
	existing: T | None = registry.get(path)
	existing_data: JsonDict = existing.data if existing else {}
	if not condition(existing_data):
		return None

	new_data: JsonDict = data.data if isinstance(data, JsonFile) else data
	if not overwrite and existing_data:
		new_data = super_merge_dict(existing_data, new_data)
	resource: T = set_json_encoder(file_type(new_data), max_level=max_level)
	registry[path] = resource
	return resource


def write_advancement(
	path: str,
	advancement: Advancement | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True, # pyright: ignore[reportUnknownLambdaType]
) -> Advancement | None:
	""" Write an advancement (ex: "namespace:folder/name"), see write_json_resource for the options. """
	return write_json_resource(Mem.ctx.data.advancements, Advancement, path, advancement, overwrite, max_level, condition)


def write_predicate(
	path: str,
	predicate: Predicate | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True, # pyright: ignore[reportUnknownLambdaType]
) -> Predicate | None:
	""" Write a predicate (ex: "namespace:is_sneaking"), see write_json_resource for the options. """
	return write_json_resource(Mem.ctx.data.predicates, Predicate, path, predicate, overwrite, max_level, condition)


def write_enchantment(
	path: str,
	enchantment: Enchantment | JsonDict,
	overwrite: bool = False,
	max_level: int = -1,
	condition: Callable[[JsonDict], bool] = lambda existing_data: True, # pyright: ignore[reportUnknownLambdaType]
) -> Enchantment | None:
	""" Write an enchantment (ex: "namespace:lifesteal"), see write_json_resource for the options. """
	return write_json_resource(Mem.ctx.data.enchantments, Enchantment, path, enchantment, overwrite, max_level, condition)

