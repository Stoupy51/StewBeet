""" What a custom block is made of: its vanilla host, its drops and growth, how it is mined, and the projectile tuning of a weapon. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass
from typing import Literal

from beet import ItemTag, LootTable
from stouputils.typing import JsonDict

from .._utils import StMapping
from ..resource import Resource

# Constants
MODEL_MARGIN: float = 1.002
""" The default `VanillaBlock.margin`: about 1/60 of a pixel on each side of a full block. """

MINING_LEVELS: tuple[str, ...] = ("wood", "stone", "iron", "diamond", "netherite")
""" Mining levels from the weakest, each tool of a level also mining every level below it. """

TOOL_MATERIALS: tuple[tuple[str, ...], ...] = (("wooden", "golden"), ("stone", "copper"), ("iron",), ("diamond",), ("netherite",))
""" The vanilla tool materials of each of `MINING_LEVELS`. """

MINING_HOSTS: dict[str, tuple[str, ...]] = {
	"wood": ("minecraft:cobblestone", "minecraft:stone_bricks", "minecraft:polished_deepslate", "minecraft:coal_block"),
	"stone": ("minecraft:iron_block", "minecraft:raw_iron_block", "minecraft:lapis_block", "minecraft:waxed_copper_block"),
	"iron": ("minecraft:diamond_block", "minecraft:gold_block", "minecraft:emerald_block", "minecraft:raw_gold_block"),
	"diamond": ("minecraft:obsidian", "minecraft:netherite_block", "minecraft:crying_obsidian"),
}
""" Vanilla blocks dropping themselves only when mined with a pickaxe of the level, the first being the default host. """

MACHINE_HOSTS: tuple[str, ...] = ("minecraft:furnace", "minecraft:smoker", "minecraft:blast_furnace", "minecraft:brewing_stand")
""" Hosts whose work `VanillaBlock.machine_speed` speeds up. """

LIT_HOSTS: tuple[str, ...] = ("minecraft:furnace", "minecraft:smoker", "minecraft:blast_furnace")
""" Hosts whose display shows the block's `_on` model while they burn. """

STAIRS_SHAPES: tuple[str, ...] = ("straight", "inner_left", "inner_right", "outer_left", "outer_right")
""" The `shape` a stairs host takes from its neighbours, its display showing the model's corner copy for each but the first. """


# Classes
@dataclass(frozen=True, kw_only=True, slots=True)
class Interaction:
	""" An interaction entity standing in the block, for a host that cannot be mined or targeted: barrier, structure void, light.

	Hitting it breaks the block, dropping its item unless the breaker is in creative.

	>>> Interaction(seat=0.5, hits=3)
	Interaction(width=1.01, height=1.01, seat=0.5, hits=3, hit_timeout=20, sound='minecraft:block.stone')
	"""
	width: float = 1.01
	height: float = 1.01
	""" From the bottom of the block, a little more than a block so it is targeted before the host. """
	seat: float | None = None
	""" Height above the bottom of the block a player sits at when using it, None when it is not a seat. """
	hits: int = 1
	""" Hits needed to break it, each counting only when it comes less than `hit_timeout` ticks after the previous one. """
	hit_timeout: int = 20
	sound: str = "minecraft:block.stone"
	""" Sound group played on each hit and on the break, as `<sound>.hit` and `<sound>.break`. """

@dataclass(frozen=True, kw_only=True, slots=True)
class Mining:
	""" The tool needed to get the block's item when breaking it, the block dropping nothing with a weaker one.

	>>> mining = Mining(tool="pickaxe", level="iron")
	>>> mining.tools
	['minecraft:iron_pickaxe', 'minecraft:diamond_pickaxe', 'minecraft:netherite_pickaxe']
	>>> mining.item_tag, mining.hosts[0]
	('your_namespace:mining/pickaxe_iron', 'minecraft:diamond_block')
	"""
	tool: Literal["pickaxe", "axe", "shovel", "hoe"] = "pickaxe"
	level: Literal["wood", "stone", "iron", "diamond", "netherite"] = "wood"

	@property
	def tools(self) -> list[str]:
		""" The vanilla tools of this level or a stronger one. """
		levels: tuple[tuple[str, ...], ...] = TOOL_MATERIALS[MINING_LEVELS.index(self.level):]
		return [f"minecraft:{material}_{self.tool}" for materials in levels for material in materials]

	@property
	def item_tag(self) -> Resource[ItemTag]:
		""" The item tag listing `tools`. """
		return Resource(ItemTag, f"mining/{self.tool}_{self.level}")

	@property
	def hosts(self) -> tuple[str, ...]:
		""" The vanilla hosts making vanilla itself require this tool, empty when none does. """
		return MINING_HOSTS.get(self.level, ()) if self.tool == "pickaxe" else ()

@dataclass(frozen=True, kw_only=True, slots=True)
class RangedWeapon:
	""" How a bow or a crossbow shoots, through a hidden enchantment the item carries.

	>>> RangedWeapon(charge_time=2.5, damage_multiplier=1.5, ammunition="bolt").name
	'Heavy Draw'
	"""
	charge_time: float | None = None
	""" Seconds a crossbow takes to load, vanilla's being 1.25. """
	damage_multiplier: float = 1.0
	""" Applied to the damage of the arrows it shoots. """
	ammunition: str | None = None
	""" The only item of the definitions a crossbow loads, anything else being given back. """
	name: str = "Heavy Draw"
	""" What the tooltip calls its enchantment, red as a curse so a grindstone keeps it. """

@dataclass(kw_only=True, slots=True)
class VanillaBlock(StMapping):
	""" Represents a vanilla block with explicit facing semantics.

	This class separates block orientation into two independent axes:
	- ``block_facing``: controls the orientation of the placed vanilla block itself
	- ``visual_facing``: controls the orientation of the visual entity/display

	Legacy ``apply_facing`` field is still accepted for backward compatibility:
	- ``apply_facing=True`` -> ``block_facing="player"``, ``visual_facing="player"``
	- ``apply_facing="entity"`` -> ``visual_facing="player"``
	- ``apply_facing=False`` -> no change (defaults)

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

	A slab taking its half from where the player clicks:

	>>> VanillaBlock(id="oak_slab", half="click").half_property
	'type'
	>>> VanillaBlock(id="oak_stairs", half="click").half_property
	'half'
	"""  # stp: ignore[long-docstring]
	id: str | None = ""
	""" The vanilla block ID, e.g. 'minecraft:stone', "minecraft:conduit[waterlogged=false]". """
	contents: bool = False
	""" For blocks using item frames and no vanilla block, e.g. servo inserter/extractor from SimplEnergy. """
	block_facing: Literal[False, "player"] = False
	""" Whether to rotate the placed vanilla block based on player orientation ([facing=...] blockstate). """
	visual_facing: Literal["none", "player", "item_frame"] = "none"
	""" Source of the visual orientation.
	"none" is no rotation, "player" gives 4 horizontal directions, "item_frame" gives 6 from the item frame's Facing.
	"""
	apply_facing: Literal[False, True, "entity", None] = None
	""" Legacy field for backward compatibility. Prefer ``block_facing`` and ``visual_facing``. """
	half: Literal["click"] | None = None
	""" "click" takes the top or bottom state of a slab, stairs or trapdoor host from the half of the block the player clicked. """
	interaction: Interaction | None = None
	""" An interaction entity breaking the block when hit, for an invisible host such as "minecraft:barrier". """
	uvlock: bool = False
	""" With visual_facing="player", show a copy of the model turned for each direction instead of turning the display.
	Its textures then keep the world grid, as `uvlock` does.
	"""
	margin: float = MODEL_MARGIN
	""" Scale of each element of the displayed model about its own center, so none of its faces lies on one of the host. 1.0: none. """
	machine_speed: float | None = None
	""" How many times faster a host of `MACHINE_HOSTS` cooks or brews. """

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
		if self.uvlock and self.visual_facing != "player":
			raise ValueError("uvlock=True turns the model by the player's facing, it needs visual_facing=\"player\".")
		if self.machine_speed is not None and self.base_id not in MACHINE_HOSTS:
			raise ValueError(f"machine_speed only speeds up {', '.join(MACHINE_HOSTS)}, not {self.id!r}.")
		if self.half and not self.base_id.endswith(("_slab", "_stairs", "_trapdoor")):
			raise ValueError(f"half=\"click\" sets the half of a slab, stairs or trapdoor host, not of {self.id!r}.")

	@property
	def base_id(self) -> str:
		""" The id without its states or data, empty for an item frame block. """
		return (self.id or "").split("[")[0].split("{")[0]

	@property
	def half_property(self) -> str:
		""" The state holding the half: `type` for a slab, `half` for stairs and trapdoors. """
		return "type" if self.base_id.endswith("_slab") else "half"

	@property
	def host_states(self) -> dict[str, str]:
		""" The host states that change after placement, each with the suffix of the model copy the display shows in it.

		>>> VanillaBlock(id="oak_stairs").host_states["shape=outer_left"], VanillaBlock(id="furnace").host_states
		('_outer_left', {'lit=false': '', 'lit=true': '_on'})
		"""
		if self.base_id.endswith("_stairs"):
			return {f"shape={shape}": "" if shape == "straight" else f"_{shape}" for shape in STAIRS_SHAPES}
		return {"lit=false": "", "lit=true": "_on"} if self.base_id in LIT_HOSTS else {}

@dataclass(kw_only=True, slots=True)
class NoSilkTouchDrop(StMapping):
	""" Defines deterministic drops when the block is broken without silk touch.

	>>> nsd = NoSilkTouchDrop(id="raw_iron")
	>>> nsd.id
	'raw_iron'
	>>> nsd.count, nsd.experience
	(1, 0.0)
	>>> NoSilkTouchDrop(loot_table="my_ns:blocks/ruby_ore", experience=2.5).loot_table
	'my_ns:blocks/ruby_ore'
	"""
	id: str = ""
	""" The item ID to drop when the block is broken without silk touch, e.g. 'raw_simplunium'.
	Empty when `loot_table` drops instead.
	"""
	loot_table: LootTable | str | None = None
	""" (Optional) A loot table, or its path, dropping instead of `id` and `count`, rolled with the breaker's tool. """
	count: dict[str, int] | int = 1
	""" (Optional) The count of items to drop. Can be an integer or a dict with 'min' and 'max' keys. Default is 1. """
	experience: dict[str, int] | float = 0.0
	""" (Optional) Experience points dropped with it, like vanilla ores do, as a dict with 'min' and 'max' keys or a number.
	The fractional part of a number is the chance of one more point: 0.5 gives 1 point half of the time.
	"""

	def __post_init__(self) -> None:
		assert bool(self.id) != (self.loot_table is not None), "A NoSilkTouchDrop drops either an item id or a loot table."
		for value in (self.count, self.experience):
			if isinstance(value, dict):
				assert "min" in value and "max" in value, "If count or experience is a dict, it must contain 'min' and 'max' keys."

@dataclass(kw_only=True, slots=True)
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

@dataclass(kw_only=True, slots=True)
class GrowingSeed(StMapping):
	""" Defines a seed that grows over time (Stardust Seed from Stardust Fragment).

	>>> gs = GrowingSeed(
	...     texture_basename="stardust", seconds=480, planted_on="diamond_block", loots=[GrowingSeedLoot(id="stardust_fragment")]
	... )
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


# Constants
VANILLA_BLOCK_FOR_ORES = VanillaBlock(id="minecraft:polished_deepslate")

