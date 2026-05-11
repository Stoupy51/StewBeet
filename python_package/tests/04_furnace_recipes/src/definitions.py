
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # SmeltingRecipe: custom ingredient → custom result
    Item(
        id="refined_ore",
        manual_category="material",
        recipes=[
            SmeltingRecipe(
                category="misc",
                experience=0.7,
                cookingtime=200,
                ingredient=Ingr("minecraft:iron_ore"),
            )
        ]
    )

    # SmeltingRecipe: custom ingredient → vanilla result
    Item(
        id="ore_piece",
        manual_category="material",
        recipes=[
            SmeltingRecipe(
                category="misc",
                experience=0.5,
                cookingtime=200,
                ingredient=Ingr("ore_piece"),
                result=Ingr("minecraft:iron_ingot"),
            )
        ]
    )

    # BlastingRecipe (faster smelting variant)
    Item(
        id="smelted_alloy",
        manual_category="material",
        recipes=[
            SmeltingRecipe(category="misc", experience=0.8, cookingtime=200, ingredient=Ingr("refined_ore")),
            BlastingRecipe(category="misc", experience=0.8, cookingtime=100, ingredient=Ingr("refined_ore")),
        ]
    )

    # SmokingRecipe: food processing
    Item(
        id="smoked_herb",
        manual_category="food",
        recipes=[
            SmokingRecipe(
                category="food",
                experience=0.35,
                cookingtime=100,
                ingredient=Ingr("minecraft:fern"),
            )
        ]
    )

    # CampfireCookingRecipe: campfire cooking
    Item(
        id="campfire_bread",
        manual_category="food",
        recipes=[
            CampfireCookingRecipe(
                category="food",
                experience=0.35,
                cookingtime=600,
                ingredient=Ingr("minecraft:wheat"),
            )
        ]
    )

    # StonecuttingRecipe: stonecutter processing
    Item(
        id="cut_stone_brick",
        manual_category="material",
        recipes=[
            StonecuttingRecipe(
                ingredient=Ingr("minecraft:stone"),
                result_count=2,
            )
        ]
    )

    # StonecuttingRecipe with a custom ingredient
    Item(
        id="polished_alloy",
        manual_category="material",
        recipes=[
            StonecuttingRecipe(
                ingredient=Ingr("smelted_alloy"),
            )
        ]
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
