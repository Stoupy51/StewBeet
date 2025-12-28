
# Imports
from dataclasses import dataclass
from typing import Literal, cast

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
    """ Represents a vanilla block with optional facing and contents. """
    id: str = ""
    """ The vanilla block ID, e.g. 'minecraft:stone', "minecraft:conduit[waterlogged=false]". """
    apply_facing: Literal[False, True, "entity"] = False
    """ Whether the block should apply facing when placed. """
    contents: bool = False
    """ For blocks using item frames and no vanilla block, e.g. servo inserter/extractor from SimplEnergy. """

    def __post_init__(self) -> None:
        if ":" not in self.id and self.id != "":
            self.id = "minecraft:" + self.id

@dataclass(kw_only=True)
class NoSilkTouchDrop(StMapping):
    """ Defines the item dropped when the block is broken without silk touch. """
    id: str
    """ The item ID to drop when the block is broken without silk touch, e.g. 'raw_simplunium'. """
    count: dict[str, int] | int = 1
    """ (Optional) The count of items to drop. Can be an integer or a dict with 'min' and 'max' keys. Default is 1. """

    def __post_init__(self) -> None:
        if isinstance(self.count, dict):
            assert "min" in self.count and "max" in self.count, "If count is a dict, it must contain 'min' and 'max' keys."

@dataclass(kw_only=True)
class GrowingSeedLoot(StMapping):
    """ Defines a single loot entry for a growing seed. """
    id: str
    """ The item ID to drop, e.g. "stardust_fragment", "minecraft:stone". """
    rolls: JsonDict | int = 1
    """ (Optional) The roll definition for the loot, e.g. {"type":"minecraft:uniform","min":3,"max":9}. """
    fortune: JsonDict | None = None
    """ (Optional) The fortune modifier for the loot, e.g. {"extra":0,"probability":0.5}. """

@dataclass(kw_only=True)
class GrowingSeed(StMapping):
    """ Defines a seed that grows over time (Stardust Seed from Stardust Fragment). """
    texture_basename: str
    """ The base name of the texture for the growing seed, e.g. 'stardust'. """
    seconds: int
    """ The time in seconds it takes for the seed to grow, e.g. 480. """
    planted_on: str
    """ The block ID on which the seed can be planted, e.g. 'diamond_block'. """
    loots: list[GrowingSeedLoot]
    """ The list of loot definitions for the seed when it is harvested. """

    def __post_init__(self) -> None:
        if self.planted_on.startswith("minecraft:"):
            self.planted_on = self.planted_on.replace("minecraft:", "", 1)


# Class
@dataclass(kw_only=True)
class Block(Item):
    base_item: str = CUSTOM_BLOCK_VANILLA
    """ Can either be CUSTOM_BLOCK_VANILLA, CUSTOM_BLOCK_ALTERNATIVE, CUSTOM_BLOCK_HEAD, or a vanilla block like 'minecraft:stone'. """

    # Specific to Block class
    vanilla_block: VanillaBlock
    """ If the block is based on a vanilla block, this defines which one and whether to apply facing. """
    no_silk_touch_drop: NoSilkTouchDrop | str | None = None
    """ (Optional) Defines the item dropped when the block is broken without silk touch, e.g. NoSilkTouchDrop(id="raw_simplunium") or just "raw_simplunium". """

    def __post_init__(self) -> None:
        from ..__memory__ import Mem

        # Add additional data to the custom blocks
        if self.id == CUSTOM_BLOCK_VANILLA:
            self.components["container"] = [
                {"slot":0,"item":{"id":"minecraft:stone","count":1,"components":{"minecraft:custom_data":{"smithed":{"block":{"id":f"{Mem.ctx.project_id}:{self.id}","from":Mem.ctx.project_id}}}}}}
            ]

            # Hide the container tooltip
            if not self.components.get("tooltip_display"):
                self.components["tooltip_display"] = {"hidden_components": []}
            elif not self.components["tooltip_display"].get("hidden_components"):
                self.components["tooltip_display"]["hidden_components"] = []
            hidden_components = cast(list[str], self.components["tooltip_display"]["hidden_components"])
            hidden_components.append("minecraft:container")

        # Add additional data to the custom blocks alternative
        elif self.id == CUSTOM_BLOCK_ALTERNATIVE:
            self.components["entity_data"] = {"id":"minecraft:item_frame","Tags":[f"{Mem.ctx.project_id}.new",f"{Mem.ctx.project_id}.{self.id}"],"Invisible":True,"Silent":True}
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
    base_item = CUSTOM_BLOCK_ALTERNATIVE

@dataclass(kw_only=True)
class BlockHead(Block):
    base_item = CUSTOM_BLOCK_HEAD

