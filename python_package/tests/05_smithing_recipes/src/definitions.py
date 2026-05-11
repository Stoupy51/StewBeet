
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # SmithingTransformRecipe: upgrade a base item using a template and addition
    Item(
        id="netherite_alloy_sword",
        manual_category="weapons",
        recipes=[
            SmithingTransformRecipe(
                template=Ingr("minecraft:netherite_upgrade_smithing_template"),
                base=Ingr("minecraft:diamond_sword"),
                addition=Ingr("minecraft:netherite_ingot"),
            )
        ]
    )

    # SmithingTransformRecipe: upgrade to custom result
    Item(
        id="alloy_chestplate",
        manual_category="armor",
        recipes=[
            SmithingTransformRecipe(
                template=Ingr("minecraft:netherite_upgrade_smithing_template"),
                base=Ingr("minecraft:diamond_chestplate"),
                addition=Ingr("minecraft:blaze_rod"),
                result=Ingr("alloy_chestplate"),
            )
        ]
    )

    # SmithingTrimRecipe: apply a trim pattern to armor
    Item(
        id="trimmed_helmet",
        manual_category="armor",
        recipes=[
            SmithingTrimRecipe(
                template=Ingr("minecraft:spire_armor_trim_smithing_template"),
                base=Ingr("minecraft:iron_helmet"),
                addition=Ingr("minecraft:diamond"),
                pattern="minecraft:spire_armor_trim_smithing_template",
            )
        ]
    )

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
