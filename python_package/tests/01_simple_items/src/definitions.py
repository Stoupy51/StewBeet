
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Basic item with all explicit components
    Item(
        id="basic_item",
        base_item="minecraft:stick",
        manual_category="tools",
        components={
            "item_name": {"text": "Basic Item", "color": "gold"},
            "lore": [{"text": "A basic test item", "italic": True, "color": "gray"}],
            "max_stack_size": 32,
        }
    )

    # Item that will get auto-generated name and lore
    Item(
        id="auto_name_item",
        base_item="minecraft:paper",
        manual_category="materials",
        components={"max_stack_size": 64}
    )

    # Item with skip_gives=True (excluded from give_all chests and loot tables)
    Item(
        id="unobtainable_item",
        base_item="minecraft:barrier",
        skip_gives=True,
        manual_category="miscellaneous",
    )

    # Item with wiki_buttons for in-game manual
    Item(
        id="wiki_item",
        base_item="minecraft:book",
        manual_category="miscellaneous",
        wiki_buttons=[
            WikiButton([
                {"text": "This is a wiki button", "color": "yellow"},
                {"text": "\nExtra info below.", "color": "white"},
            ]),
            WikiButton({"text": "Another standalone button", "color": "aqua"}),
        ],
    )

    # Item with explicit custom_data component
    Item(
        id="tracked_item",
        base_item="minecraft:iron_ingot",
        manual_category="material",
        components={
            "custom_data": {ns: {"tracked_item": True}},
            "item_name": {"text": "Tracked Item"},
        }
    )

    # Final adjustments
    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
