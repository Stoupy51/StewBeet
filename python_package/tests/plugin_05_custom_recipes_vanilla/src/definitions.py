
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Item with a 2x2 shaped recipe
    Item(
        id="shaped_item",
        base_item="minecraft:gold_ingot",
        manual_category="misc",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["XX", "XX"],
                ingredients={"X": Ingr("minecraft:gold_nugget")},
            )
        ],
    )

    # Item with a shapeless recipe (vanilla result -> item produced by vanilla engine)
    Item(
        id="shapeless_item",
        base_item="minecraft:paper",
        manual_category="misc",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[Ingr("minecraft:string"), Ingr("minecraft:string")],
            )
        ],
    )

    # Item with a stonecutting recipe
    Item(
        id="stone_slab",
        base_item="minecraft:stone_slab",
        manual_category="misc",
        recipes=[
            StonecuttingRecipe(
                ingredient=Ingr("minecraft:stone"),
                result_count=2,
            )
        ],
    )

    # Item with a SmithingTransform recipe
    Item(
        id="smithed_item",
        base_item="minecraft:netherite_sword",
        manual_category="misc",
        recipes=[
            SmithingTransformRecipe(
                template=Ingr("minecraft:netherite_upgrade_smithing_template"),
                base=Ingr("minecraft:diamond_sword"),
                addition=Ingr("minecraft:netherite_ingot"),
            )
        ],
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
