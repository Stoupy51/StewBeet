
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Define an ExternalItem from another datapack with predicate-based matching
    ExternalItem(
        id="otherplugin:special_ingot",
        custom_data_predicate={"smithed": {"dict": {"ingot": {"special": True}}}, "otherplugin": {"id": "special_ingot"}},
        components={
            "item_name": {"text": "Special Ingot"},
            "lore": [{"text": "From another datapack", "italic": True, "color": "gray"}],
        },
        loot_table="otherplugin:items/special_ingot",
    )

    # Define an ExternalItem with minimal config (just id and predicate)
    ExternalItem(
        id="otherplugin:rare_gem",
        custom_data_predicate={"otherplugin": {"rare_gem": True}},
    )

    # Define a local item that uses the ExternalItem as a recipe ingredient
    Item(
        id="hybrid_tool",
        manual_category="tools",
        recipes=[
            CraftingShapedRecipe(
                category="misc",
                shape=["SGS", " S "],
                ingredients={
                    "S": Ingr("otherplugin:special_ingot"),
                    "G": Ingr("minecraft:gold_ingot"),
                },
            )
        ]
    )

    # Local item using ExternalItem in a shapeless recipe
    Item(
        id="gem_infused_item",
        manual_category="material",
        recipes=[
            CraftingShapelessRecipe(
                category="misc",
                ingredients=[
                    Ingr("otherplugin:rare_gem"),
                    Ingr("minecraft:iron_ingot"),
                ],
            )
        ]
    )

    # Apply name/lore/data to local items only (not external)
    add_item_name_and_lore_if_missing()
    add_item_name_and_lore_if_missing(is_external=True)
    add_private_custom_data_for_namespace()

