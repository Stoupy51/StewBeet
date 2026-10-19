
# Imports
from beet import Context

from stewbeet import *


# Main entry point
def beet_default(ctx: Context):
	# Block with id but NO facing -> simple setblock, no rotation
	Block(
		id="block_no_facing",
		manual_category="misc",
		vanilla_block=VanillaBlock(id="minecraft:cobblestone"),
	)

	# Block with visual_facing="player" -> item_display rotates, no block facing state
	Block(
		id="block_visual_facing",
		manual_category="misc",
		vanilla_block=VanillaBlock(id="minecraft:glass", visual_facing="player"),
	)

	# Block with block_facing="player" -> vanilla block gets facing= blockstate AND display rotates
	Block(
		id="block_with_facing",
		manual_category="misc",
		vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player"),
	)

	# BlockAlternative (item_frame, contents) with default facing
	BlockAlternative(
		id="block_contents",
		manual_category="misc",
		vanilla_block=VanillaBlock(contents=True),
	)

	# Ore dropping a vanilla item and experience unless mined with silk touch
	Block(
		id="block_ore_experience",
		manual_category="misc",
		vanilla_block=VANILLA_BLOCK_FOR_ORES,
		no_silk_touch_drop=NoSilkTouchDrop(id="minecraft:diamond", experience={"min": 3, "max": 7}),
	)

	add_item_model_component()
	add_item_name_and_lore_if_missing()
	add_private_custom_data_for_namespace()
	add_smithed_ignore_vanilla_behaviours_convention()

