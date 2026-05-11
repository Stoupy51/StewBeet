
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Define the ore blocks that will be generated in the world
    Block(
        id="test_ore",
        manual_category="blocks",
        vanilla_block=VanillaBlock(id="minecraft:stone"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:stone")])],
    )

    Block(
        id="deepslate_test_ore",
        manual_category="blocks",
        vanilla_block=VanillaBlock(id="minecraft:deepslate"),
        recipes=[CraftingShapelessRecipe(category="blocks", ingredients=[Ingr("minecraft:deepslate")])],
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
