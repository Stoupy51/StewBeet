
# Imports
from dataclasses import dataclass, field
from typing import Any

from beet.core.utils import JsonDict, TextComponent

from ..constants import (
    CATEGORY,
    CUSTOM_ITEM_VANILLA,
    OVERRIDE_MODEL,
    RESULT_OF_CRAFTING,
    USED_FOR_CRAFTING,
    WIKI_COMPONENT,
)
from ._recipe_list import RecipeList
from ._utils import StMapping
from .recipe import RecipeBase
from .wiki_button import WikiButton


# Class
@dataclass(kw_only=True)
class Item(StMapping):
    """ Represents an item with a unique identifier.

    ## Simple example
    >>> from stewbeet import Mem
    >>> item = Item(id="multimeter", base_item="minecraft:warped_fungus_on_a_stick")
    >>> item.id
    'multimeter'
    >>> item.base_item
    'minecraft:warped_fungus_on_a_stick'
    >>> item.id in Mem.definitions
    True
    >>> item is Item.from_id("multimeter")
    True

    ## Instance without registration in Mem.definitions
    >>> nonreg_item = Item(id="")   # Item with empty ID won't be registered
    >>> nonreg_item.id = "temporary_item"
    >>> "temporary_item" in Mem.definitions
    False
    >>> nonreg_item is Item.from_id("temporary_item", strict=False)
    False

    ## Big example with all fields
    >>> from stewbeet import CraftingShapedRecipe, WikiButton, Ingr
    >>> obj = Item(
    ...     id="stardust_ingot",
    ...     base_item="minecraft:raw_iron",
    ...     manual_category="materials",
    ...     recipes=[
    ...         CraftingShapedRecipe(shape=["###","#F#","###"], ingredients={"#":Ingr("stardust_fragment"),"F":Ingr("minecraft:iron_ingot")})
    ...     ],
    ...     override_model={"parent":"item/generated","textures":{"layer0":"stardust:item/stardust_ingot"}},
    ...     wiki_buttons=[WikiButton({"text":"This is a stardust ingot.","color":"aqua"})],
    ...     components={
    ...         "item_name": {"text":"Stardust Ingot","color":"aqua"},
    ...         "max_stack_size": 99,
    ...     }
    ... )
    >>> also_obj = Item.from_id("stardust_ingot")
    >>> obj is also_obj
    True
    """

    id: str
    """ Unique identifier for the item, e.g. 'multimeter', 'simplunium_block'. """
    base_item: str = CUSTOM_ITEM_VANILLA
    """ Represents an item with a unique identifier, e.g 'minecraft:command_block'. """
    manual_category: str | None = None
    """ (Optional) manual category for organizing items in the ingame-manual. """
    recipes: list[RecipeBase] = field(default_factory=list[RecipeBase])
    """ (Optional) List of recipes associated with this item. """
    override_model: JsonDict | None = None
    """ (Optional) Merge with/Override auto-generated item model (based on the textures folder). """
    hand_model: JsonDict | None = None
    """ (Optional) If None, hand_model will be the same model as override_model. """
    wiki_buttons: list[WikiButton] | TextComponent | None = None
    """ (Optional) Additional informations to be displayed in the ingame manual. """
    components: JsonDict = field(default_factory=dict[str, Any])
    """ (Optional) Additional custom components for this item, e.g. "item_name": {...}, etc. """

    # Register item in memory
    def __post_init__(self) -> None:
        # Add minecraft: to base item if needed
        if self.base_item and ":" not in self.base_item:
            self.base_item = "minecraft:" + self.base_item

        ## Fix some fields
        # Convert recipes to RecipeList for automatic normalization
        self.recipes = RecipeList(self.id, self.recipes)

        # Fix !component values
        self.components = {k.replace("minecraft:", ""): v for k, v in self.components.items()}
        for k, v in self.components.items():
            if k.startswith("!") and v != {}:
                self.components[k] = {}

        # Register the item in the global definitions (if not external)
        from ..__memory__ import Mem
        if self.id and ":" not in self.id and self.id not in Mem.definitions:
            Mem.definitions[self.id] = self

    # Mapping methods (__getitem__, __len__, and __iter__)
    def _get_mapping(self) -> JsonDict:
        mapping: JsonDict = {
            CATEGORY: self.manual_category,
            RESULT_OF_CRAFTING: self.recipes,
            USED_FOR_CRAFTING: self.recipes,
            OVERRIDE_MODEL: self.override_model,
            WIKI_COMPONENT: self.wiki_buttons,
        }
        mapping.update(self.components)
        return mapping

    def __getitem__(self, key: str) -> Any:
        mapping: JsonDict = self._get_mapping()
        return mapping.get(key, getattr(self, key))

    def __len__(self) -> int:
        return len(self._get_mapping())

    def __iter__(self):
        return iter(self._get_mapping())

    def update(self, other: JsonDict) -> None:
        for key, value in other.items():
            if key in self._get_mapping():
                setattr(self, key, value)

