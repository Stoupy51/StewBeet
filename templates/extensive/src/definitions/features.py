
# Imports
from stouputils.typing import JsonDict

from stewbeet import *  # type: ignore


# Functions
def box(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> JsonDict:
	""" A model element with the texture "#t" on its six faces. """
	return {"from": [x1, y1, z1], "to": [x2, y2, z2], "faces": {side: {"texture": "#t"} for side in ("north", "south", "east", "west", "up", "down")}}


def shape(texture: str, *elements: JsonDict) -> JsonDict:
	""" A block model made of `elements` all drawn with one texture of the textures folder. """
	return {"parent": "block/block", "textures": {"t": f"{Mem.ctx.project_id}:item/{texture}", "particle": f"{Mem.ctx.project_id}:item/{texture}"}, "elements": list(elements)}


# Main entry point
def main():

	# A seat on an invisible barrier host: right click sits, 3 hits with an iron pickaxe or better break it
	Block(
		id="chair",
		vanilla_block=VanillaBlock(id="minecraft:barrier", visual_facing="player", interaction=Interaction(seat=0.5, hits=3, sound="minecraft:block.wood")),
		override_model=shape(
			"cherry_planks",
			box(3, 6.5, 3, 13, 8, 13), box(3, 0, 3, 4.5, 6.5, 4.5), box(11.5, 0, 3, 13, 6.5, 4.5),
			box(3, 0, 11.5, 4.5, 6.5, 13), box(11.5, 0, 11.5, 13, 6.5, 13), box(3, 8, 11.5, 13, 16, 13),
		),
		mining=Mining(level="iron"),
	)

	# No host given: StewBeet picks the default host of the mining level
	Block(id="crate", override_model=shape("crate", box(0, 0, 0, 16, 16, 16)), mining=Mining(level="iron"))

	# Halves taken from where the player clicks, stairs facing the way the player looks, textures kept on the world grid
	Block(id="plank_slab", vanilla_block=VanillaBlock(id="minecraft:oak_slab", half="click"), override_model=shape("cherry_planks", box(0, 0, 0, 16, 8, 16)))
	Block(
		id="plank_stairs",
		vanilla_block=VanillaBlock(id="minecraft:oak_stairs", block_facing="player", half="click", uvlock=True),
		override_model=shape("cherry_planks", box(0, 0, 0, 16, 8, 16), box(0, 8, 8, 16, 16, 16)),
	)

	# A furnace cooking twice as fast, its display slightly bigger than the host (margin 1.0 would leave its size)
	Block(id="fast_furnace", vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player", machine_speed=2.0, margin=1.005))

	# An ore dropping a loot table with experience, its drop vanishing when broken with too weak a pickaxe
	Block(
		id="ruby_ore",
		vanilla_block=VANILLA_BLOCK_FOR_ORES,
		no_silk_touch_drop=NoSilkTouchDrop(
			loot_table=LootTable({"pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:raw_iron"}]}]}),
			experience={"min": 2, "max": 4},
		),
		mining=Mining(level="iron"),
	)

	# A light without collision
	Block(
		id="lamp",
		vanilla_block=VanillaBlock(id="minecraft:light[level=15]", interaction=Interaction()),
		override_model=shape("lamp", box(5, 0, 5, 11, 1, 11), box(4, 1, 4, 12, 9, 12), box(5, 9, 5, 11, 10, 11), box(7, 10, 7, 9, 13, 9)),
	)

	# A drink giving its mug back (a stack of 16 gives 15 drinks and the mug) and 30 seconds of nausea
	Item(id="beer_mug")
	nausea: JsonDict = {"type": "minecraft:apply_effects", "effects": [{"id": "minecraft:nausea", "duration": 30 * 20}]}
	Item(id="beer", remainder="beer_mug", components={"max_stack_size": 16, "consumable": {"on_consume_effects": [nausea]}})

	# A crossbow loading only its bolts
	Item(id="bolt", base_item="minecraft:arrow")
	Item(
		id="crossbow", base_item="minecraft:crossbow",
		ranged_weapon=RangedWeapon(charge_time=2.5, damage_multiplier=1.5, ammunition="bolt"),
	)

