
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Case 5: Contents with native item_frame facing (6 directions from the frame's Facing NBT)
    BlockAlternative(
        id="vb_contents",
        manual_category="blocks",
        vanilla_block=VanillaBlock(contents=True),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:item_frame")])],
    )

    # Case 6: Contents with player-overridden facing — get_rotation is called while
    #         @s=player in the search function, then ItemRotation is applied (4 dirs)
    BlockAlternative(
        id="vb_contents_player",
        manual_category="blocks",
        vanilla_block=VanillaBlock(contents=True, visual_facing="player"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:item_frame"), Ingr("minecraft:compass")])],
    )

    # Case 7: Contents with explicit item_frame facing (6 directions, same underlying
    #         behaviour as Case 5 but uses the "item_frame" value explicitly)
    BlockAlternative(
        id="vb_contents_frame",
        manual_category="blocks",
        vanilla_block=VanillaBlock(contents=True, visual_facing="item_frame"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:item_frame"), Ingr("minecraft:string")])],
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
