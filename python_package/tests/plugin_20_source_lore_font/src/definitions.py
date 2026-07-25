
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # One item is enough: last_final only creates the font when an item actually carries the source lore
    Item(id="branded_item", base_item="minecraft:diamond", manual_category="misc")

    add_item_name_and_lore_if_missing()
