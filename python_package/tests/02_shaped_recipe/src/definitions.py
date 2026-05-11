
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # 3x3 shaped recipe: all same vanilla ingredient → custom result
    Item(
        id="compressed_iron",
        manual_category="material",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["III", "III", "III"],
                ingredients={"I": Ingr("minecraft:iron_ingot")},
            )
        ]
    )

    # 2x2 shaped recipe: custom ingredient → custom result
    Item(
        id="double_compressed_iron",
        manual_category="material",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["CC", "CC"],
                ingredients={"C": Ingr("compressed_iron")},
            )
        ]
    )

    # Shaped recipe with multiple different vanilla ingredients (2x2)
    Item(
        id="wood_essence",
        manual_category="material",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=[" L ", "LLL", " L "],
                ingredients={"L": Ingr("minecraft:oak_log")},
            )
        ]
    )

    # Shaped recipe with explicit vanilla result (not the item being defined)
    Item(
        id="catalyst",
        manual_category="material",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["GGG", "GDG", "GGG"],
                ingredients={"G": Ingr("minecraft:gold_ingot"), "D": Ingr("minecraft:diamond")},
                result=Ingr("minecraft:nether_star"),
                result_count=1,
            )
        ]
    )

    # Shaped recipe producing multiple items (result_count > 1)
    Item(
        id="split_stone",
        manual_category="material",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["SS"],
                ingredients={"S": Ingr("minecraft:stone")},
                result_count=4,
            )
        ]
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
