
# Imports
from dataclasses import dataclass
from typing import Literal

import stouputils as stp
from beet import LootTable
from stouputils.typing import JsonDict

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
    """ Represents a vanilla block with explicit facing semantics.

    This class separates block orientation into two independent axes:
    - ``block_facing``: controls the orientation of the placed vanilla block itself
    - ``visual_facing``: controls the orientation of the visual entity/display

    Legacy ``apply_facing`` field is still accepted for backward compatibility:
    - ``apply_facing=True`` → ``block_facing="player"``, ``visual_facing="player"``
    - ``apply_facing="entity"`` → ``visual_facing="player"``
    - ``apply_facing=False`` → no change (defaults)

    Default behavior (no facing):

    >>> vb = VanillaBlock(id="minecraft:stone")
    >>> vb.id
    'minecraft:stone'
    >>> vb.block_facing
    False
    >>> vb.visual_facing
    'none'

    Legacy ``apply_facing=True`` (block + visual rotation):

    >>> vb = VanillaBlock(id="minecraft:furnace", apply_facing=True)
    >>> vb.block_facing
    'player'
    >>> vb.visual_facing
    'player'

    Legacy ``apply_facing="entity"`` (visual only):

    >>> vb = VanillaBlock(id="minecraft:stone", apply_facing="entity")
    >>> vb.block_facing
    False
    >>> vb.visual_facing
    'player'

    Item frame custom block (no rotation):

    >>> vb = VanillaBlock(contents=True)
    >>> vb.contents
    True
    >>> vb.id is None
    True
    >>> vb.visual_facing
    'none'

    Item frame rotated like player (4 horizontal directions):

    >>> vb = VanillaBlock(contents=True, visual_facing="player")
    >>> vb.visual_facing
    'player'

    Item frame using its own facing (6 directions):

    >>> vb = VanillaBlock(contents=True, visual_facing="item_frame")
    >>> vb.visual_facing
    'item_frame'

    Invalid: ``block_facing`` with ``contents=True``:

    >>> VanillaBlock(contents=True, block_facing="player")
    Traceback (most recent call last):
    ...
    ValueError: contents=True cannot use block_facing="player"; use visual_facing instead.

    New fields directly:

    >>> vb = VanillaBlock(id="minecraft:barrel", block_facing="player")
    >>> vb.block_facing
    'player'
    >>> vb.visual_facing
    'player'
    """
    id: str | None = ""
    """ The vanilla block ID, e.g. 'minecraft:stone', "minecraft:conduit[waterlogged=false]". """
    contents: bool = False
    """ For blocks using item frames and no vanilla block, e.g. servo inserter/extractor from SimplEnergy. """
    block_facing: Literal[False, "player"] = False
    """ Whether to rotate the placed vanilla block based on player orientation ([facing=...] blockstate). """
    visual_facing: Literal["none", "player", "item_frame"] = "none"
    """ Source of the visual orientation: "none" (no rotation), "player" (4 horizontal directions), "item_frame" (6 directions from item frame Facing). """
    apply_facing: Literal[False, True, "entity", None] = None
    """ Legacy field for backward compatibility. Prefer ``block_facing`` and ``visual_facing``. """

    def __post_init__(self) -> None:
        # Normalize ID
        if self.id and ":" not in self.id:
            self.id = "minecraft:" + self.id

        # Handle contents mode (item_frame backend)
        if self.contents:
            self.id = None

        # Legacy compatibility: apply_facing -> new fields
        if self.apply_facing is True:
            self.block_facing = "player"
            self.visual_facing = "player"
        elif self.apply_facing == "entity":
            self.visual_facing = "player"

        # Implicit: block_facing="player" implies visual_facing="player" unless explicitly set
        if self.block_facing == "player" and self.visual_facing == "none" and self.apply_facing is None:
            self.visual_facing = "player"

        # Validation
        if self.contents and self.block_facing:
            raise ValueError("contents=True cannot use block_facing=\"player\"; use visual_facing instead.")

@dataclass(kw_only=True)
class NoSilkTouchDrop(StMapping):
    """ Defines deterministic drops when the block is broken without silk touch.

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
    ...     vanilla_block=VanillaBlock(id="minecraft:wheat"),
    ...     no_silk_touch_drop=NoSilkTouchDrop(id="stardust_fragment", count=1),
    ...     growing_seed=GrowingSeed(
    ...         texture_basename="stardust",
    ...         seconds=480,
    ...         planted_on="diamond_block",
    ...         loots=[GrowingSeedLoot(id="stardust_fragment", rolls=3)]
    ...     ),
    ...     on_place="tag @s add seed"
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
    no_silk_touch_drop: NoSilkTouchDrop | LootTable | str | None = None
    """ (Optional) No-silk drop mode: deterministic (e.g. `NoSilkTouchDrop(id="raw_simplunium")` or string item id "raw_simplunium") or dynamic (`LootTable` object from beet). """
    on_place: str | None = None
    """ (Optional) Text to append to the function ``{ns}:custom_blocks/{id}/place_secondary`` that is executed on block placement as the item display """

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
            hidden_components: list[str] = self.components.setdefault("tooltip_display", {}).setdefault("hidden_components", [])
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
VANILLA_BLOCK_FOR_ORES = VanillaBlock(id="minecraft:polished_deepslate")

