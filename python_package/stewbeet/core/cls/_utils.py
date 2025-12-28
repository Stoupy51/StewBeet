
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
                if isinstance(data_dict[new], list) and isinstance(data_dict[old], list):
                    stp.unique_list([data_dict[new], *data_dict.pop(old)])
                else:
                    # TODO: Remove this
                    raise TypeError(f"Cannot merge fields '{old}' and '{new}' as they are not both lists.")
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

        return cls(**known_kwargs)

    @classmethod
    def from_id(cls, item_id: str) -> Self:
        """ Create an object based of definitions. If ':' is in item_id, it's in external_definitions """
        from ..__memory__ import Mem
        if ":" not in item_id:
            return cls.from_dict(Mem.definitions[item_id], item_id)
        else:
            return cls.from_dict(Mem.external_definitions[item_id], item_id)

