
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Normal item — must appear in individual and creative loot tables
    Item(id="obtainable", base_item="minecraft:diamond", manual_category="misc")

    # Item with skip_gives=True — must NOT appear in any loot table
    Item(id="hidden", base_item="minecraft:barrier", skip_gives=True, manual_category="misc")

    # Item whose recipe produces x4 — requires an extra count-variant loot table
    Item(
        id="bulk_item",
        base_item="minecraft:iron_ingot",
        manual_category="misc",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[Ingr("minecraft:iron_nugget")],
                result_count=4,
            )
        ],
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
