
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Case 1: No facing at all — block and item_display use default orientation
    Block(
        id="vb_no_facing",
        manual_category="blocks",
        vanilla_block=VanillaBlock(id="minecraft:cobblestone"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:cobblestone")])],
    )

    # Case 2: Visual-only rotation — item_display rotates with the player (4 horizontal dirs),
    #         but the underlying vanilla block is placed without a facing blockstate
    Block(
        id="vb_visual_facing",
        manual_category="blocks",
        vanilla_block=VanillaBlock(id="minecraft:glass", visual_facing="player"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:glass")])],
    )

    # Case 3: Block + visual rotation — vanilla block gets facing= blockstate AND
    #         the item_display rotates (implicit visual_facing="player")
    Block(
        id="vb_block_facing",
        manual_category="blocks",
        vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:furnace")])],
    )

    # Case 4: Block + visual rotation WITH extra blockstates — plugin must preserve
    #         "lit=false" while still appending "facing=<dir>"
    Block(
        id="vb_block_states",
        manual_category="blocks",
        vanilla_block=VanillaBlock(id="minecraft:furnace[lit=false]", block_facing="player"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:furnace"), Ingr("minecraft:coal")])],
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
