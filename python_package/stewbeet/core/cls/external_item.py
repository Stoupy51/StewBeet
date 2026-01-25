
# Imports
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
    """
    id: str
    """ Unique identifier for the item, e.g. 'mechanization:raw_tin', 'simplenergy:machine_block'. """
    custom_data_predicate: JsonDict = field(default_factory=dict[str, Any])
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

