
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Item produced by smelting iron ore
    Item(
        id="smelted_bar",
        base_item="minecraft:iron_ingot",
        manual_category="misc",
        recipes=[
            SmeltingRecipe(
                experience=0.7,
                cookingtime=200,
                category="misc",
                ingredient=Ingr("minecraft:raw_iron"),
            ),
            BlastingRecipe(
                experience=0.7,
                cookingtime=100,
                category="misc",
                ingredient=Ingr("minecraft:raw_iron"),
            ),
        ],
    )

    # Item produced by smoking
    Item(
        id="smoked_food",
        base_item="minecraft:cooked_beef",
        manual_category="misc",
        recipes=[
            SmokingRecipe(
                experience=0.35,
                cookingtime=100,
                category="food",
                ingredient=Ingr("minecraft:beef"),
            ),
        ],
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
