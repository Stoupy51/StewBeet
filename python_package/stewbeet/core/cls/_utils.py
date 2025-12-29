
# Imports
from collections.abc import Mapping
from dataclasses import dataclass, fields
from typing import Any, Self

import stouputils as stp
from beet.core.utils import JsonDict

from ..constants import NOT_COMPONENTS


# Class for mapping behavior
@dataclass
class StMapping(Mapping[str, Any]):
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
    def __setitem__(self, key: str, value: Any) -> None:
        return setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except (KeyError, AttributeError):
            return default

    def setdefault(self, key: str, default: Any = None) -> Any:
        """ Set a default value if key doesn't exist, like dict.setdefault(). """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def to_dict(self) -> JsonDict:
        """ Convert the object to a dictionary for JSON serialization """
        from dataclasses import asdict, is_dataclass

        def _convert_value(value: Any) -> Any:
            """ Recursively convert a value to a JSON-serializable form """
            if value is None:
                return None
            elif hasattr(value, 'to_dict'):
                return value.to_dict()
            elif is_dataclass(value) and not isinstance(value, type):
                return asdict(value)
            elif isinstance(value, list):
                return [_convert_value(item) for item in value] # pyright: ignore[reportUnknownVariableType]
            elif isinstance(value, dict):
                return {k: _convert_value(v) for k, v in value.items()} # pyright: ignore[reportUnknownVariableType]
            else:
                return value

        result: JsonDict = {}
        for field_info in fields(self):
            value = getattr(self, field_info.name)
            if value is not None:
                result[field_info.name] = _convert_value(value)
        return result

    @classmethod
    def from_dict(cls, data: JsonDict | "StMapping", item_id: str) -> Self:
        """ Create an object based on items """
        if isinstance(data, cls):
            return data

        # Make a copy to avoid modifying the original
        # Rename some fields from StewBeet v2.x to v3.x
        rename_dict: dict[str, str] = {
            "id": "base_item",
            "category": "manual_category",
            "result_of_crafting": "recipes",
            "used_for_crafting": "recipes",
            "wiki_components": "wiki_buttons",
        }
        data_dict: JsonDict = dict(data)
        for old, new in rename_dict.items():
            if old in data_dict and new not in data_dict:
                data_dict[new] = data_dict.pop(old)
            elif old in data_dict and new in data_dict:
                if data_dict[new] == data_dict[old]:
                    data_dict.pop(old)
                elif isinstance(data_dict[new], list) and isinstance(data_dict[old], list):
                    data_dict[new] = stp.unique_list([*data_dict[new], *data_dict.pop(old)])
                else:
                    # TODO: Remove this
                    raise TypeError(f"Cannot merge fields '{old}' and '{new}' as they are not both lists. Value of '{new}': {data_dict[new]}, value of '{old}': {data_dict[old]}")
        data_dict["id"] = item_id

        # Get valid field names for this class
        valid_fields: set[str] = {f.name for f in fields(cls)}

        # Separate known fields from unknown fields
        known_kwargs: JsonDict = {}
        unknown_kwargs: JsonDict = {}
        for key, value in data_dict.items():
            if key in valid_fields:
                known_kwargs[key] = value
            else:
                unknown_kwargs[key] = value

        # If there are unknown fields and the class has a 'components' field, add them there
        if unknown_kwargs and "components" in valid_fields:
            # Merge with existing components if any
            existing_components = known_kwargs.get('components', {})
            if isinstance(existing_components, dict):
                known_kwargs["components"] = {**existing_components, **unknown_kwargs}
            else:
                known_kwargs["components"] = unknown_kwargs
        elif unknown_kwargs:
            # If no components field exists, raise an error
            raise TypeError(f"{cls.__name__}() got unexpected keyword arguments: {', '.join(unknown_kwargs.keys())}")

        # Remove unexpected components keys (from StewBeet)
        for key in NOT_COMPONENTS:
            if "components" in known_kwargs and key in known_kwargs["components"]:
                del known_kwargs["components"][key]

        # Add empty vanilla_block if needed
        if "vanilla_block" in valid_fields:
            if "vanilla_block" not in known_kwargs:
                known_kwargs["vanilla_block"] = ""

        # Create the instance
        return cls(**known_kwargs)

    @classmethod
    def from_id(cls, item_id: str, strict: bool = True) -> Self:
        """ Create an object based of definitions. If ':' is in item_id, it's in external_definitions

        Args:
            item_id	(str):		The item ID to create the object from.
            strict	(bool):		Whether to raise an error if the item is not found.
        """
        from ..__memory__ import Mem
        if strict:
            if ":" not in item_id:
                return cls.from_dict(Mem.definitions[item_id], item_id)
            else:
                return cls.from_dict(Mem.external_definitions[item_id], item_id)
        else:
            if ":" not in item_id:
                return cls.from_dict(Mem.definitions.get(item_id, {}), item_id)
            else:
                return cls.from_dict(Mem.external_definitions.get(item_id, {}), item_id)

    def copy(self) -> JsonDict:
        """ Return a shallow copy as a dictionary. """
        return self.to_dict()

    # Mapping methods (__len__ and __iter__)
    def __len__(self) -> int:
        return len(self.to_dict())
    def __iter__(self):
        return iter(self.to_dict())

