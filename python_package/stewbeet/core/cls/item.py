
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

import stouputils as stp
from beet import ItemModel, LootTable, Model, Recipe, Texture
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ..constants import (
    CATEGORY,
    CUSTOM_ITEM_VANILLA,
    ITEMS_LOOT_FOLDER,
    OVERRIDE_MODEL,
    RESULT_OF_CRAFTING,
    USED_FOR_CRAFTING,
    WIKI_COMPONENT,
)
from ..utils.loot_table import result_count_to_suffix
from ._recipe_list import RecipeList
from ._utils import StMapping
from .recipe import RecipeBase
from .resource import Resource
from .wiki_button import WikiButton

if TYPE_CHECKING:
    from ...plugins.sniffer.model import SourceOrigin


# Class
@dataclass(kw_only=True, slots=True)
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

    ## Resource locations (namespace falls back to "your_namespace" outside a build)
    >>> obj.loot_table
    'your_namespace:i/stardust_ingot'
    >>> obj.loot_table_for(5)
    'your_namespace:i/stardust_ingot_x5'
    >>> obj.loot_table_for({"min": 4, "max": 6})
    'your_namespace:i/stardust_ingot_x4to6'
    >>> obj.item_model
    'your_namespace:stardust_ingot'
    >>> obj.model
    'your_namespace:item/stardust_ingot'
    >>> obj.texture
    'your_namespace:item/stardust_ingot'
    >>> obj.recipe(), obj.recipe(2)
    ('your_namespace:stardust_ingot', 'your_namespace:stardust_ingot_2')

    A user-defined "item_model" component wins, but the generated file location doesn't move:
    >>> obj.components["item_model"] = "minecraft:air"
    >>> obj.item_model
    'minecraft:air'
    >>> obj.generated_item_model
    'your_namespace:stardust_ingot'
    >>> del obj.components["item_model"]
    """

    id: str
    """ Unique identifier for the item, e.g. 'multimeter', 'simplunium_block'. """
    base_item: str = CUSTOM_ITEM_VANILLA
    """ Represents an item with a unique identifier, e.g 'minecraft:recovery_compass'. """
    manual_category: str | None = None
    """ (Optional) manual category for organizing items in the ingame-manual. """
    recipes: list[RecipeBase] = field(default_factory=list[RecipeBase])
    """ (Optional) List of recipes associated with this item. """
    override_model: JsonDict | None = None
    """ (Optional) Merge with/Override auto-generated item model (based on the textures folder). """
    DEFAULT_OVERRIDE_MODEL_CONTEXTS: ClassVar[list[str]] = ["none", "fixed"]
    """ Default display contexts in which the regular model is kept when a hand_model is defined (item display entities and item frames). """

    hand_model: JsonDict | None = None
    """ (Optional) Model used instead of the regular model in most display contexts (hand, gui, ground, ...), see override_model_contexts. If None, the item uses the same model everywhere. """
    override_model_contexts: list[str] | None = None
    """ (Optional) When hand_model is set, display contexts in which the regular model is still used (default: DEFAULT_OVERRIDE_MODEL_CONTEXTS, i.e. item display entities and item frames). """
    wiki_buttons: list[WikiButton] | TextComponent | None = None
    """ (Optional) Additional informations to be displayed in the ingame manual. """
    components: JsonDict = field(default_factory=dict[str, Any])
    """ (Optional) Additional custom components for this item, e.g. "item_name": {...}, etc. """
    skip_gives: bool = False
    """ (Optional) If True, loot tables and give_all chests won't give this item. Useful for items that are never meant to be obtained by players. """
    origin: SourceOrigin | None = field(default=None, init=False, repr=False, compare=False, metadata={"transient": True})
    """ Where this definition was declared, captured by the sniffer plugin so content a plugin generates
    from it maps back to the declaration instead of to the plugin. None unless that plugin is active. """

    # Register item in memory
    def __post_init__(self) -> None:
        # Captured here because this is the only moment the declaring frame is still on the stack.
        from ..__memory__ import Mem
        if Mem.sniffer_enabled:
            from ...plugins import sniffer
            self.origin = sniffer.resolve_origin()

        # Add minecraft: to base item if needed
        if self.base_item and ":" not in self.base_item:
            self.base_item = "minecraft:" + self.base_item
        if ":" in self.id:
            stp.warning(
                f"Item ID '{self.id}' cannot contain ':', these characters are reserved for external item definitions. "
                "Please remove the namespace from the ID or use ExternalItem if that's what you meant."
            )
            self.id = self.id.split(":")[-1]

        # Warnings
        if self.wiki_buttons and not self.manual_category:
            stp.warning(f"Item '{self.id}' has wiki_buttons but no manual_category. It won't be displayed in the ingame manual.")

        ## Fix some fields
        # Convert recipes to RecipeList for automatic normalization
        self.recipes = RecipeList(self.id, self.recipes)

        # Fix !component values
        self.components = {k.replace("minecraft:", ""): v for k, v in self.components.items()}
        for k, v in self.components.items():
            if k.startswith("!") and v != {}:
                self.components[k] = {}

        # Register the item in the global definitions (if not external)
        if self.id and ":" not in self.id and self.id not in Mem.definitions:
            Mem.definitions[self.id] = self

    # Resource locations
    def loot_table_for(self, result_count: int | JsonDict) -> Resource[LootTable]:
        """ Get the loot table giving this item in the requested amount.

        Args:
            result_count (int|JsonDict): The amount to give, ex: 1, 5, {"min":4,"max":6}
        Returns:
            Resource[LootTable]: The loot table, ex: "your_namespace:i/stardust_ingot_x5"
        """
        return Resource(LootTable, f"{ITEMS_LOOT_FOLDER}/{self.id}{result_count_to_suffix(result_count)}")

    @property
    def loot_table(self) -> Resource[LootTable]:
        """ The loot table giving one of this item, ex: "your_namespace:i/stardust_ingot". """
        return self.loot_table_for(1)

    @property
    def item_model(self) -> Resource[ItemModel]:
        """ The item model this item renders as, honoring the "item_model" component when set.

        Beware: this is what the item points to, which the user can override to anything.
        Use `generated_item_model` for the location StewBeet actually writes the file at.
        """
        override: Any = self.components.get("item_model")
        if override:
            return Resource(ItemModel, str(override))
        return self.generated_item_model

    @property
    def generated_item_model(self) -> Resource[ItemModel]:
        """ The item model location StewBeet generates for this item, ex: "your_namespace:stardust_ingot". """
        return Resource(ItemModel, self.id)

    @property
    def model(self) -> Resource[Model]:
        """ The model generated for this item, ex: "your_namespace:item/stardust_ingot". """
        return Resource(Model, f"item/{self.id}")

    @property
    def texture(self) -> Resource[Texture]:
        """ The main texture of this item, ex: "your_namespace:item/stardust_ingot". """
        return Resource(Texture, f"item/{self.id}")

    def recipe(self, index: int = 1) -> Resource[Recipe]:
        """ Get the vanilla recipe file of this item.

        Args:
            index (int): The recipe number when the item has multiple vanilla recipes (1-based)
        Returns:
            Resource[Recipe]: The recipe, ex: "your_namespace:stardust_ingot" or "your_namespace:stardust_ingot_2"
        """
        return Resource(Recipe, self.id if index <= 1 else f"{self.id}_{index}")

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

