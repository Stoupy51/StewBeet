
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Item with a 3x3 shaped recipe (requires Smithed Crafter)
    Item(
        id="shaped_custom",
        base_item="minecraft:stick",
        manual_category="misc",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["XXX", "XYX", "XXX"],
                ingredients={
                    "X": Ingr("minecraft:stone"),
                    "Y": Ingr("minecraft:diamond"),
                },
            )
        ],
    )

    # Item with a shapeless recipe that uses two different custom-data ingredients
    Item(
        id="shapeless_custom",
        base_item="minecraft:iron_nugget",
        manual_category="misc",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[
                    Ingr("shaped_custom"),   # custom item ingredient
                    Ingr("minecraft:flint"),
                ],
                result_count=3,
            )
        ],
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
