""" Definitions behind the landing page hero.

The `hero-snippet` region below is what the website shows. Two things read this file:
scripts/prehighlight.ts extracts that region, dedents it and runs Shiki over it, and
python_package/scripts/build_hero_output.py builds this project and records every file it produced.

Lines inside the region are kept under 66 columns once dedented. The snippet sits in half the hero
and anything longer is cut mid-string on a 1280px screen, which reads as a rendering bug rather
than as scrollable code. prehighlight.ts enforces that budget and fails the build if it is broken.

Indentation here is 4 spaces, not tabs like the rest of the package: this file is rendered as-is on
the landing page, and a browser tab stop is 8 columns, which would blow the width budget.

Adapted from the life_crystal_block of Stardust Fragment: the EQUIPMENT constant is inlined and the
long override_model dropped, from src/definitions/additions/equipments.py, and the ore generation
call is folded in from src/utils/custom_ore_generation.py, where that project keeps it.
"""
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # The crystal the block drops and is crafted from. Outside the region: the hero is about
    # the block, and an ingredient item beside it would only dilute the snippet.
    Item(
        id="life_crystal",
        manual_category="equipment",
        components={"item_name": {"text": "Life Crystal"}},
    )

    # region hero-snippet
    Block(
        id="life_crystal_block",
        vanilla_block=VanillaBlock(id="minecraft:glass"),
        manual_category="equipment",
        components={
            "item_name": {"text": "Life Crystal Block"},
            "lore": [{"text": "Break it to get the crystal back"}],
        },
        # Broken without Silk Touch, it hands the crystal back
        no_silk_touch_drop=NoSilkTouchDrop(
            id="life_crystal", count=1,
        ),
        recipes=[CraftingShapelessRecipe(
            category="equipment", result_count=1,
            ingredients=8 * [Ingr("minecraft:glass")]
                + [Ingr("life_crystal")],
        )],
    )
    # Single-block veins, deep in the overworld, carved into stone
    CustomOreGeneration.all_with_config({
        "life_crystal_block": [CustomOreGeneration(
        dimensions=["minecraft:overworld"],
        minimum_height=-32, maximum_height=50,
        veins_per_region=1.5,
        provider=["#minecraft:overworld_carver_replaceables"],
    )]})
    # endregion hero-snippet

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
