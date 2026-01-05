
# Imports
from dataclasses import dataclass
from typing import Literal

import stouputils as stp
from beet.core.utils import JsonDict

from ..constants import (
    CUSTOM_BLOCK_ALTERNATIVE,
    CUSTOM_BLOCK_HEAD,
    CUSTOM_BLOCK_VANILLA,
    NO_SILK_TOUCH_DROP,
    VANILLA_BLOCK,
)
from ._utils import StMapping
from .item import Item


# Subclasses
@dataclass(kw_only=True)
class VanillaBlock(StMapping):
    """ Represents a vanilla block with optional facing and contents.

    >>> vb = VanillaBlock(id="minecraft:stone")
    >>> vb.id
    'minecraft:stone'
    >>> vb.apply_facing
    False
    """
    id: str = ""
    """ The vanilla block ID, e.g. 'minecraft:stone', "minecraft:conduit[waterlogged=false]". """
    apply_facing: Literal[False, True, "entity"] = False
    """ Whether the block should apply facing when placed. """
    contents: bool = False
    """ For blocks using item frames and no vanilla block, e.g. servo inserter/extractor from SimplEnergy. """

    def __post_init__(self) -> None:
        if ":" not in self.id and self.id != "":
            self.id = "minecraft:" + self.id
        if self.contents:
            self.id = self.apply_facing = None

@dataclass(kw_only=True)
class NoSilkTouchDrop(StMapping):
    """ Defines the item dropped when the block is broken without silk touch.

    >>> nsd = NoSilkTouchDrop(id="raw_iron")
    >>> nsd.id
    'raw_iron'
    >>> nsd.count
    1
    """
    id: str
    """ The item ID to drop when the block is broken without silk touch, e.g. 'raw_simplunium'. """
    count: dict[str, int] | int = 1
    """ (Optional) The count of items to drop. Can be an integer or a dict with 'min' and 'max' keys. Default is 1. """

    def __post_init__(self) -> None:
        if isinstance(self.count, dict):
            assert "min" in self.count and "max" in self.count, "If count is a dict, it must contain 'min' and 'max' keys."

@dataclass(kw_only=True)
class GrowingSeedLoot(StMapping):
    """ Defines a single loot entry for a growing seed.

    >>> gsl = GrowingSeedLoot(id="stardust_fragment", rolls=3)
    >>> gsl.id
    'stardust_fragment'
    >>> gsl.rolls
    3
    """
    id: str
    """ The item ID to drop, e.g. "stardust_fragment", "minecraft:stone". """
    rolls: JsonDict | int = 1
    """ (Optional) The roll definition for the loot, e.g. {"type":"minecraft:uniform","min":3,"max":9}. """
    fortune: JsonDict | None = None
    """ (Optional) The fortune modifier for the loot, e.g. {"extra":0,"probability":0.5}. """

@dataclass(kw_only=True)
class GrowingSeed(StMapping):
    """ Defines a seed that grows over time (Stardust Seed from Stardust Fragment).

    >>> gs = GrowingSeed(texture_basename="stardust", seconds=480, planted_on="diamond_block", loots=[GrowingSeedLoot(id="stardust_fragment")])
    >>> gs.texture_basename
    'stardust'
    >>> gs.seconds
    480
    """
    texture_basename: str
    """ The base name of the texture for the growing seed, e.g. 'stardust'. """
    seconds: int
    """ The time in seconds it takes for the seed to grow, e.g. 480. """
    planted_on: str
    """ The block ID on which the seed can be planted, e.g. 'diamond_block'. """
    loots: list[GrowingSeedLoot] | str
    """ The list of loot definitions for the seed when it is harvested, or a loot path path. """

    def __post_init__(self) -> None:
        if self.planted_on.startswith("minecraft:"):
            self.planted_on = self.planted_on.replace("minecraft:", "", 1)


# Class
@dataclass(kw_only=True)
class Block(Item):
    """ Represents a block item with vanilla block properties.

    ## Simple example
    >>> from stewbeet import Mem
    >>> block = Block(id="machine_block", vanilla_block=VanillaBlock(id="minecraft:stone"))
    >>> block.id
    'machine_block'
    >>> block.vanilla_block.id
    'minecraft:stone'
    >>> block.id in Mem.definitions
    True
    >>> block is Block.from_id("machine_block")
    True

    ## Big example with all fields
    >>> from stewbeet import CraftingShapelessRecipe, WikiButton, NoSilkTouchDrop, GrowingSeed, GrowingSeedLoot, Ingr
    >>> obj = BlockAlternative(
    ...     id="stardust_seed",
    ...     manual_category="miscellaneous",
    ...     recipes=[
    ...         CraftingShapelessRecipe(ingredients=8*[Ingr("stardust_fragment")] + [Ingr("minecraft:wheat_seeds")])
    ...     ],
    ...     override_model={"parent":"item/generated","textures":{"layer0":"stardust:item/stardust_seed"}},
    ...     wiki_buttons=[WikiButton({"text":"A magical seed that grows stardust.","color":"aqua"})],
    ...     components={
    ...         "item_name": {"text":"Stardust Seed","color":"aqua"},
    ...         "max_stack_size": 64,
    ...     },
    ...     vanilla_block=VanillaBlock(id="minecraft:wheat", apply_facing=False),
    ...     no_silk_touch_drop=NoSilkTouchDrop(id="stardust_fragment", count=1),
    ...     growing_seed=GrowingSeed(
    ...         texture_basename="stardust",
    ...         seconds=480,
    ...         planted_on="diamond_block",
    ...         loots=[GrowingSeedLoot(id="stardust_fragment", rolls=3)]
    ...     )
    ... )
    >>> also_obj = Block.from_id("stardust_seed")
    >>> obj is also_obj
    True
    """
    base_item: str = CUSTOM_BLOCK_VANILLA
    """ Can either be CUSTOM_BLOCK_VANILLA, CUSTOM_BLOCK_ALTERNATIVE, CUSTOM_BLOCK_HEAD, or a vanilla block like 'minecraft:stone'. """

    # Specific to Block class
    vanilla_block: VanillaBlock
    """ If the block is based on a vanilla block, this defines which one and whether to apply facing. """
    no_silk_touch_drop: NoSilkTouchDrop | str | None = None
    """ (Optional) Defines the item dropped when the block is broken without silk touch, e.g. NoSilkTouchDrop(id="raw_simplunium") or just "raw_simplunium". """

    # Others
    growing_seed: GrowingSeed | None = None
    """ (Optional) Defines a seed that grows over time (Stardust Seed from Stardust Fragment). """

    def __post_init__(self) -> None:
        from ..__memory__ import Mem
        ns: str = Mem.ctx.project_id if Mem.ctx else "your_namespace"

        # Add additional data to the custom blocks
        if self.base_item == CUSTOM_BLOCK_VANILLA:
            self.components["container"] = [
                {"slot":0,"item":{"id":"minecraft:stone","count":1,"components":{"minecraft:custom_data":{"smithed":{"block":{"id":f"{ns}:{self.id}","from":ns}}}}}}
            ]

            # Hide the container tooltip
            if not self.components.get("tooltip_display"):
                self.components["tooltip_display"] = {"hidden_components": []}
            elif not self.components["tooltip_display"].get("hidden_components"):
                self.components["tooltip_display"]["hidden_components"] = []
            hidden_components: list[str] = self.components["tooltip_display"]["hidden_components"]
            hidden_components.append("minecraft:container")
            self.components["tooltip_display"]["hidden_components"] = stp.unique_list(hidden_components)

        # Add additional data to the custom blocks alternative
        elif self.base_item == CUSTOM_BLOCK_ALTERNATIVE:
            self.components["entity_data"] = {"id":"minecraft:item_frame","Tags":[f"{ns}.new",f"{ns}.{self.id}"],"Invisible":True,"Silent":True}
        super().__post_init__()

    # Mapping methods
    def _get_mapping(self) -> JsonDict:
        mapping: JsonDict = super()._get_mapping()
        mapping.update({
            VANILLA_BLOCK: self.vanilla_block,
            NO_SILK_TOUCH_DROP: self.no_silk_touch_drop,
        })
        return mapping

@dataclass(kw_only=True)
class BlockAlternative(Block):
    """ Represents a block that uses an item frame for placement (e.g., servo inserter/extractor).

    >>> ba = BlockAlternative(id="servo_inserter", vanilla_block=VanillaBlock(contents=True))
    >>> ba.base_item
    'minecraft:item_frame'
    """
    base_item = CUSTOM_BLOCK_ALTERNATIVE
    def __post_init__(self) -> None:
        self.base_item = CUSTOM_BLOCK_ALTERNATIVE
        super().__post_init__()

@dataclass(kw_only=True)
class BlockHead(Block):
    """ Represents a block that uses a player head for placement.

    >>> bh = BlockHead(id="custom_head", vanilla_block=VanillaBlock(id="minecraft:player_head"))
    >>> bh.base_item
    'minecraft:player_head'
    """
    base_item = CUSTOM_BLOCK_HEAD
    def __post_init__(self) -> None:
        self.base_item = CUSTOM_BLOCK_HEAD
        super().__post_init__()

# Constants
VANILLA_BLOCK_FOR_ORES = VanillaBlock(id="minecraft:polished_deepslate", apply_facing=False)

