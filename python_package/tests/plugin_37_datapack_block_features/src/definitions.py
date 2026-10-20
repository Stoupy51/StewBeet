
# Imports
from beet import Context, LootTable
from stouputils.typing import JsonDict

from stewbeet import *


# Main entry point
def beet_default(ctx: Context):
	# A seat on a barrier, broken in 3 hits with an iron pickaxe at least
	Block(
		id="bf_seat",
		vanilla_block=VanillaBlock(id="minecraft:barrier", interaction=Interaction(seat=0.5, hits=3, sound="minecraft:block.metal")),
		mining=Mining(level="iron"),
	)

	# No host given: the default host of the iron level
	Block(id="bf_storage", mining=Mining(level="iron"))

	# Halves taken from where the player clicks, stairs facing the way the player looks with turned models
	Block(id="bf_slab", vanilla_block=VanillaBlock(id="minecraft:oak_slab", half="click"))
	steps: list[JsonDict] = [{"from": [0, 0, 0], "to": [16, 8, 16]}, {"from": [0, 8, 8], "to": [16, 16, 16]}]
	Block(
		id="bf_stairs", vanilla_block=VanillaBlock(id="minecraft:oak_stairs", block_facing="player", half="click", uvlock=True),
		override_model={"parent": "block/block", "textures": {"all": f"{ctx.project_id}:item/bf_stairs"}, "elements": [
			{**step, "faces": {side: {"texture": "#all"} for side in ("north", "south", "east", "west", "up", "down")}}
			for step in steps
		]},
	)

	# A furnace cooking twice as fast, shown lit while it burns
	Block(id="bf_furnace", vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player", machine_speed=2.0))

	# An ore dropping a loot table with experience, its item vanishing with a stone pickaxe
	Block(
		id="bf_ore",
		vanilla_block=VANILLA_BLOCK_FOR_ORES,
		no_silk_touch_drop=NoSilkTouchDrop(
			loot_table=LootTable({"pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:raw_iron"}]}]}),
			experience={"min": 2, "max": 4},
		),
		mining=Mining(level="iron"),
	)

	# An emissive block without collision
	Block(id="bf_lamp", vanilla_block=VanillaBlock(id="minecraft:light[level=15]", interaction=Interaction()))

	# A drink giving its mug back, and a crossbow loading bolts only
	Item(id="bf_mug")
	Item(id="bf_drink", remainder="bf_mug", components={"max_stack_size": 16, "consumable": {}})
	Item(id="bf_bolt", base_item="minecraft:arrow")
	Item(
		id="bf_crossbow", base_item="minecraft:crossbow",
		ranged_weapon=RangedWeapon(charge_time=2.5, damage_multiplier=1.5, ammunition="bf_bolt"),
	)

	add_item_model_component()
	add_item_name_and_lore_if_missing()
	add_private_custom_data_for_namespace()
	add_smithed_ignore_vanilla_behaviours_convention()

