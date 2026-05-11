
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Shapeless recipe: combine multiple vanilla items → custom result
    Item(
        id="alloy_dust",
        manual_category="material",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[
                    Ingr("minecraft:coal"),
                    Ingr("minecraft:iron_ingot"),
                    Ingr("minecraft:gravel"),
                ],
            )
        ]
    )

    # Shapeless recipe with 9 identical items (block compression pattern)
    Item(
        id="alloy_block",
        manual_category="material",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=9 * [Ingr("alloy_dust")],
            )
        ]
    )

    # Shapeless recipe that decompresses a block into 9 units
    Item(
        id="decompressed_alloy",
        manual_category="material",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[Ingr("alloy_block")],
                result=Ingr("alloy_dust"),
                result_count=9,
            )
        ]
    )

    # Self-recipe: put the item in the crafting grid to "update" it
    Item(
        id="upgradable_item",
        manual_category="material",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[Ingr("upgradable_item")],
            )
        ]
    )

    # Shapeless recipe: mixed custom and vanilla ingredients
    Item(
        id="mixed_alloy",
        manual_category="material",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[
                    Ingr("alloy_dust"),
                    Ingr("minecraft:gold_nugget"),
                    Ingr("minecraft:gold_nugget"),
                ],
            )
        ]
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
