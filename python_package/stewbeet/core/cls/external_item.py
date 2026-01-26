
# Imports
import json
from dataclasses import dataclass, field
from typing import Any

from beet.core.utils import JsonDict

from ._utils import StMapping
from .item import Item


# Class
@dataclass
class ExternalItem(StMapping):
    """ Represents an item from an external datapack.

    Examples:
        >>> obj = ExternalItem(
        ...     id="mechanization:raw_tin",
        ...     base_item="minecraft:structure_block",
        ...     custom_data_predicate={"smithed": {"dict": {"raw": {"tin": True}}}, "mechanization": {"id": "raw_tin"}},
        ...     components={
        ...         "item_name": {"text": "Raw Tin"},
        ...         "lore": [{"text": "A chunk of unrefined tin."}],
        ...     },
        ...     loot_table="mechanization:base/tin_raw",
        ... )
        >>> obj.loot_table
        'mechanization:base/tin_raw'

        >>> obj = ExternalItem("simplenergy:machine_block", custom_data_predicate={"simplenergy": {"machine_block": True}})
        >>> obj.id
        'simplenergy:machine_block'

        >>> obj = ExternalItem(
        ...     id="custom_namespace:custom_item",
    """
    id: str
    """ Unique identifier for the item, e.g. 'mechanization:raw_tin', 'simplenergy:machine_block'. """
    custom_data_predicate: JsonDict | str
    """ Predicate to use for matching custom data when used in recipes, e.g. {"smithed": {"dict": {"raw": {"tin": True}}}}. """
    components: JsonDict = field(default_factory=dict[str, Any])
    """ Additional components for the item, e.g. {"item_name": {"text": "Raw Tin"}, "lore": [{"text": "Some lore"}]}. """
    loot_table: str | None = None
    """ (Optional) Loot table path to use to get the item, e.g. "mechanization:base/tin_raw". """
    base_item: str = Item.base_item
    """ (Optional) Base item identifier, e.g. "minecraft:poisonous_potato". """


    # Register item in memory
    def __post_init__(self) -> None:

        # Fix !component values
        self.components = {k.replace("minecraft:", ""): v for k, v in self.components.items()}
        for k, v in self.components.items():
            if k.startswith("!") and v != {}:
                self.components[k] = {}

        # Register the item in the global definitions (if not external)
        from ..__memory__ import Mem
        if self.id and self.id not in Mem.external_definitions:
            Mem.external_definitions[self.id] = self

    # Json dump with custom handling
    @staticmethod
    def json_dump(obj: Any) -> Any:
        """ Custom JSON dump function to prevent escaping of certain fields. """
        obj = json.loads(json.dumps(obj))   # Deep copy

        # Replace some string fields with placeholders
        fields: JsonDict = {}
        def replace_field(value: JsonDict) -> Any:
            for k, v in value.items():
                if isinstance(v, list):
                    value[k] = [replace_field(i) for i in v] # type: ignore
                elif isinstance(v, dict):
                    value[k] = replace_field(v) # type: ignore
                elif isinstance(v, str) and k == "minecraft:custom_data":
                    placeholder = f"__PLACEHOLDER_{len(fields)}__"
                    fields[placeholder] = v
                    value[k] = placeholder
            return value
        obj = replace_field(obj)

        # Dump to JSON and replace placeholders with original values
        json_str: str = json.dumps(obj)
        for placeholder, original in fields.items():
            json_str = json_str.replace(f'"{placeholder}"', original)

        # Return final JSON string
        return json_str

