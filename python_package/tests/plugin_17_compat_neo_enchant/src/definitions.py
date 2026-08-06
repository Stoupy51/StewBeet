
# Imports
from beet import Context

from stewbeet import *  # type: ignore
from stewbeet.core.cls.block import VANILLA_BLOCK_FOR_ORES


# Main entry point
def beet_default(ctx: Context):
    # Two ore blocks using VANILLA_BLOCK_FOR_ORES (polished_deepslate placeholder)
    Block(
        id="ruby_ore",
        manual_category="misc",
        vanilla_block=VANILLA_BLOCK_FOR_ORES,
    )
    Block(
        id="deepslate_ruby_ore",
        manual_category="misc",
        vanilla_block=VANILLA_BLOCK_FOR_ORES,
    )

    # A regular block (not an ore): must NOT affect the veinminer tag
    Block(
        id="ruby_block",
        manual_category="misc",
        vanilla_block=VanillaBlock(id="minecraft:red_concrete"),
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
