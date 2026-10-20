
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass

import stouputils as stp
from beet import Advancement, Function, ItemModel, LootTable, Model, Texture
from stouputils.typing import JsonDict

from ...constants import (
	CUSTOM_BLOCK_ALTERNATIVE,
	CUSTOM_BLOCK_HEAD,
	CUSTOM_BLOCK_VANILLA,
	CUSTOM_BLOCKS_FOLDER,
	NO_SILK_TOUCH_DROP,
	PLAYER_HEAD_FOLDER,
	SEEDS_FOLDER,
	VANILLA_BLOCK,
)
from ..block_functions import BlockFunctions
from ..resource import Resource
from .features import GrowingSeed, Mining, NoSilkTouchDrop, VanillaBlock
from .item import Item


# Class
@dataclass(kw_only=True, slots=True)
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
	... )
	>>> also_obj = Block.from_id("stardust_seed")
	>>> obj is also_obj
	True

	## Resource locations
	>>> block.functions.place_main
	'your_namespace:custom_blocks/machine_block/place_main'
	>>> block.functions.place_secondary
	'your_namespace:custom_blocks/machine_block/place_secondary'
	>>> block.functions.destroy
	'your_namespace:custom_blocks/machine_block/destroy'
	>>> block.functions["any_custom_function"]
	'your_namespace:custom_blocks/machine_block/any_custom_function'
	>>> block.functions.folder
	'your_namespace:custom_blocks/machine_block'
	>>> block.loot_table
	'your_namespace:i/machine_block'
	>>> block.no_silk_touch_loot_table
	'your_namespace:custom_blocks/no_silk_touch_drop/machine_block'

	Growing seed stages use the seed texture basename, not the block ID:
	>>> obj.seed_stage_item_model(2)
	'your_namespace:seeds/stardust_stage_2'
	>>> obj.seed_stage_model(2)
	'your_namespace:item/seeds/stardust_stage_2'
	>>> obj.seed_loot_table
	'your_namespace:seeds/stardust_seed'

	Regular custom blocks are detected by the smithed custom_block library, so they have
	no placement advancement of their own:
	>>> block.advancement  # doctest: +ELLIPSIS
	Traceback (most recent call last):
	...
	ValueError: Block 'machine_block' uses base_item 'minecraft:furnace' and has no placement advancement (...)
	"""  # stp: ignore[long-docstring]
	base_item: str = CUSTOM_BLOCK_VANILLA
	""" Can either be CUSTOM_BLOCK_VANILLA, CUSTOM_BLOCK_ALTERNATIVE, CUSTOM_BLOCK_HEAD, or a vanilla block like 'minecraft:stone'. """

	# Specific to Block class
	vanilla_block: VanillaBlock | None = None
	""" (Optional) If the block is based on a vanilla block, this defines which one and whether to apply facing. """
	no_silk_touch_drop: NoSilkTouchDrop | LootTable | str | None = None
	""" (Optional) What drops without silk touch.
	Deterministic with `NoSilkTouchDrop(id="raw_simplunium")` or the item id "raw_simplunium", dynamic with a beet `LootTable`.
	"""
	on_place: str | None = None
	""" Deprecated since v3.5.0. """
	mining: Mining | None = None
	""" (Optional) The tool needed to get the item when breaking it.
	A real host left unset becomes the first of `Mining.hosts`, an interaction host checks the breaker's tool itself.
	"""

	# Others
	growing_seed: GrowingSeed | None = None
	""" (Optional) Defines a seed that grows over time (Stardust Seed from Stardust Fragment). """

	def __post_init__(self) -> None:
		from ...__memory__ import Mem
		ns: str = Mem.ctx.project_id

		# Deprecation warning
		if self.on_place:
			stp.warning(
				f"Block '{self.id}': 'on_place' is deprecated since v3.5.0 and will be removed in a future version. "
				f"Use Block.from_id({self.id!r}).functions.place_secondary.obj.append(...) instead, "
				"from a plugin running AFTER 'stewbeet.plugins.datapack.custom_blocks' so the commands "
				"still land after the block setup (.obj raises KeyError if you access it too early)."
			)

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
			self.components["entity_data"] = {
				"id":"minecraft:item_frame", "Tags":[f"{ns}.new",f"{ns}.{self.id}"], "Invisible":True, "Silent":True
			}
		super().__post_init__()

	# Resource locations
	@property
	def functions(self) -> BlockFunctions:
		""" The mcfunctions of this custom block, ex: `block.functions.place_secondary`. """
		return BlockFunctions(self.id)

	@property
	def no_silk_touch_loot_table(self) -> Resource[LootTable]:
		""" The loot table used when this block is broken without silk touch. """
		return Resource(LootTable, f"{CUSTOM_BLOCKS_FOLDER}/no_silk_touch_drop/{self.id}")

	@property
	def seed_loot_table(self) -> Resource[LootTable]:
		""" The loot table dropped when this growing seed is fully grown and harvested. """
		return Resource(LootTable, f"{SEEDS_FOLDER}/{self.id}")

	@property
	def alternative_advancement(self) -> Resource[Advancement]:
		""" The advancement detecting the placement of an item frame based custom block. """
		return Resource(Advancement, f"custom_block_alternative/{self.id}")

	@property
	def head_advancement(self) -> Resource[Advancement]:
		""" The advancement detecting the placement of a player head based custom block. """
		return Resource(Advancement, f"custom_block_head/{self.id}")

	@property
	def advancement(self) -> Resource[Advancement]:
		""" The advancement detecting the placement of this custom block.

		Returns:
			Resource[Advancement]: The placement advancement
		Raises:
			ValueError: If the block is a regular custom block, since those are handled by the
				smithed custom_block library instead of a per-block advancement.
		"""
		if self.base_item == CUSTOM_BLOCK_ALTERNATIVE:
			return self.alternative_advancement
		if self.base_item == CUSTOM_BLOCK_HEAD:
			return self.head_advancement
		raise ValueError(
			f"Block '{self.id}' uses base_item '{self.base_item}' and has no placement advancement "
			"(regular custom blocks are detected by the smithed custom_block library)"
		)

	@property
	def head_search(self) -> Resource[Function]:
		""" The function searching the placed player head of this custom block. """
		return Resource(Function, f"{PLAYER_HEAD_FOLDER}/search_{self.id}")

	def seed_stage_name(self, stage: str | int) -> str:
		""" Get the shared base name of a growth stage of this growing seed.

		Args:
			stage: The growth stage, ex: 0, 1, 2, ...
		Returns:
			str: The stage name, ex: "stardust_stage_2"
		"""
		basename: str = (self.growing_seed.texture_basename or self.id) if self.growing_seed else self.id
		return f"{basename}_stage_{stage}"

	def seed_stage_item_model(self, stage: str | int) -> Resource[ItemModel]:
		""" Get the item model of a growth stage of this growing seed.

		Args:
			stage: The growth stage, ex: 0, 1, 2, ...
		Returns:
			Resource[ItemModel]: The item model, ex: "your_namespace:seeds/stardust_stage_2"
		"""
		return Resource(ItemModel, f"{SEEDS_FOLDER}/{self.seed_stage_name(stage)}")

	def seed_stage_model(self, stage: str | int) -> Resource[Model]:
		""" Get the model of a growth stage of this growing seed.

		Args:
			stage: The growth stage, ex: 0, 1, 2, ...
		Returns:
			Resource[Model]: The model, ex: "your_namespace:item/seeds/stardust_stage_2"
		"""
		return Resource(Model, f"item/{SEEDS_FOLDER}/{self.seed_stage_name(stage)}")

	def seed_stage_texture(self, stage: str | int) -> Resource[Texture]:
		""" Get the texture of a growth stage of this growing seed.

		Args:
			stage: The growth stage, ex: 0, 1, 2, ...
		Returns:
			Resource[Texture]: The texture, ex: "your_namespace:item/seeds/stardust_stage_2"
		"""
		return Resource(Texture, f"item/{SEEDS_FOLDER}/{self.seed_stage_name(stage)}")

	# Mapping methods
	def _get_mapping(self) -> JsonDict:
		mapping: JsonDict = super()._get_mapping()
		mapping.update({
			VANILLA_BLOCK: self.vanilla_block,
			NO_SILK_TOUCH_DROP: self.no_silk_touch_drop,
		})
		return mapping

@dataclass(kw_only=True, slots=True)
class BlockAlternative(Block):
	""" Represents a block that uses an item frame for placement (e.g., servo inserter/extractor).

	>>> ba = BlockAlternative(id="servo_inserter", vanilla_block=VanillaBlock(contents=True))
	>>> ba.base_item
	'minecraft:item_frame'
	>>> ba.advancement
	'your_namespace:custom_block_alternative/servo_inserter'
	>>> ba.functions.search
	'your_namespace:custom_blocks/servo_inserter/search'
	"""
	def __post_init__(self) -> None:
		self.base_item = CUSTOM_BLOCK_ALTERNATIVE
		super().__post_init__()

@dataclass(kw_only=True, slots=True)
class BlockHead(Block):
	""" Represents a block that uses a player head for placement.

	>>> bh = BlockHead(id="custom_head", vanilla_block=VanillaBlock(id="minecraft:player_head"))
	>>> bh.base_item
	'minecraft:player_head'
	>>> bh.advancement
	'your_namespace:custom_block_head/custom_head'
	>>> bh.head_search
	'your_namespace:custom_blocks/_player_head/search_custom_head'
	"""
	def __post_init__(self) -> None:
		self.base_item = CUSTOM_BLOCK_HEAD
		super().__post_init__()

