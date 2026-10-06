
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields, is_dataclass
from typing import Any, Self

import stouputils as stp
from beet import LootTable
from stouputils.typing import JsonDict

from ..constants import NOT_COMPONENTS

# Constants
RENAMED_FIELDS: dict[str, str] = {
	"id": "base_item",
	"category": "manual_category",
	"result_of_crafting": "recipes",
	"used_for_crafting": "recipes",
	"wiki_components": "wiki_buttons",
}
""" Fields a StewBeet 2 definition may use, and the field of StewBeet 3 each one fills. """


def json_ready(value: Any) -> Any:
	""" A value in a JSON-serializable form: a loot table as its data, a dataclass or anything with `to_dict` as a dict.

	Lists and dicts are converted item by item.

	>>> json_ready({"a": [LootTable({"pools": []}), None]})
	{'a': [{'pools': []}, None]}
	"""
	if isinstance(value, LootTable):
		return json_ready(value.data)
	if hasattr(value, 'to_dict'):
		return value.to_dict()
	if is_dataclass(value) and not isinstance(value, type):
		return asdict(value)
	if isinstance(value, list):
		return [json_ready(item) for item in value] # pyright: ignore[reportUnknownVariableType]
	if isinstance(value, dict):
		return {k: json_ready(v) for k, v in value.items()} # pyright: ignore[reportUnknownVariableType]
	return value


# Class for mapping behavior
@dataclass(slots=True)
class StMapping(Mapping[str, Any]):
	def __getitem__(self, key: str) -> Any:
		return getattr(self, key)
	def __setitem__(self, key: str, value: Any) -> None:
		return setattr(self, key, value)
	def __contains__(self, key: Any) -> bool:
		return self.get(key) is not None

	def get(self, key: str, default: Any = None) -> Any:
		""" Like dict.get(), where a field left at None counts as absent. """
		try:
			value: Any = self[key]
		except (KeyError, AttributeError):
			return default
		return default if value is None else value

	def setdefault(self, key: str, default: Any = None) -> Any:
		""" Set a default value if key doesn't exist, like dict.setdefault(). """
		value: Any = self.get(key)
		if value is None:
			self[key] = default
			return default
		return value

	def to_dict(self) -> JsonDict:
		""" Convert the object to a dictionary for JSON serialization, transient and unset fields left out """
		return {
			field_info.name: json_ready(value)
			for field_info in fields(self)
			if not field_info.metadata.get("transient") and (value := getattr(self, field_info.name)) is not None
		}

	@classmethod
	def from_dict(cls, data: JsonDict | StMapping, item_id: str) -> Self:
		""" Create an object based on items """
		if isinstance(data, StMapping):
			return data  # pyright: ignore[reportReturnType]

		data_dict: JsonDict = dict(data)
		rename_fields(data_dict)
		data_dict["id"] = item_id

		# An unknown field is a component, for a class that has components
		valid_fields: set[str] = {f.name for f in fields(cls)}
		known_kwargs: JsonDict = {key: value for key, value in data_dict.items() if key in valid_fields}
		unknown_kwargs: JsonDict = {key: value for key, value in data_dict.items() if key not in valid_fields}
		if unknown_kwargs and "components" not in valid_fields:
			raise TypeError(f"{cls.__name__}() got unexpected keyword arguments: {', '.join(unknown_kwargs.keys())}")
		if unknown_kwargs:
			existing = known_kwargs.get('components', {})
			known_kwargs["components"] = {**existing, **unknown_kwargs} if isinstance(existing, dict) else unknown_kwargs

		# Keys StewBeet itself reads, never components
		for key in NOT_COMPONENTS:
			if "components" in known_kwargs and key in known_kwargs["components"]:
				del known_kwargs["components"][key]
		return cls(**known_kwargs)

	@classmethod
	def from_id(cls, item_id: str, strict: bool = True) -> Self:
		""" Create an object based of definitions. If ':' is in item_id, it's in external_definitions

		Args:
			item_id: The item ID to create the object from.
			strict:  Whether to raise an error if the item is not found.
		"""
		from ..__memory__ import Mem
		if strict:
			if ":" not in item_id:
				return cls.from_dict(Mem.definitions[item_id], item_id)
			return cls.from_dict(Mem.external_definitions[item_id], item_id)
		if ":" not in item_id:
			return cls.from_dict(Mem.definitions.get(item_id) or {}, item_id)
		return cls.from_dict(Mem.external_definitions.get(item_id) or {}, item_id)

	@classmethod
	def clone(cls, other: Self) -> Self:
		""" Create a clone of another instance """
		return cls(**other.to_dict())

	def copy(self) -> JsonDict:
		""" Return a shallow copy as a dictionary. """
		return self.to_dict()

	# Mapping methods (__len__ and __iter__)
	def __len__(self) -> int:
		return len(self.to_dict())
	def __iter__(self):
		return iter(self.to_dict())


def rename_fields(data: JsonDict) -> None:
	""" Move each field of `RENAMED_FIELDS` to the field it fills, merging two lists, and dropping it when both hold the same.

	>>> data = {"category": "misc", "result_of_crafting": [1], "recipes": [2], "used_for_crafting": [1, 3]}
	>>> rename_fields(data); data
	{'recipes': [2, 1, 3], 'manual_category': 'misc'}
	"""
	for old, new in RENAMED_FIELDS.items():
		if old not in data:
			continue
		if new not in data:
			data[new] = data.pop(old)
		elif data[new] == data[old]:
			data.pop(old)
		elif isinstance(data[new], list) and isinstance(data[old], list):
			data[new] = stp.unique_list([*data[new], *data.pop(old)])

