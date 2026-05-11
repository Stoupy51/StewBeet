
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Item with a recognisable name — the lang plugin must create a translate entry for it
    Item(
        id="gold_ring",
        base_item="minecraft:gold_ingot",
        manual_category="misc",
        components={
            "item_name": {"text": "Gold Ring", "color": "gold"},
            "lore": [{"text": "A shiny ring", "italic": True, "color": "gray"}],
        },
    )

    # Item that relies on add_item_name_and_lore_if_missing for auto name generation
    Item(
        id="copper_wire",
        base_item="minecraft:copper_ingot",
        manual_category="misc",
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
