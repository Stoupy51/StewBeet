
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Two items to verify storage population
    Item(id="item_alpha", base_item="minecraft:diamond", manual_category="misc")
    Item(id="item_beta", base_item="minecraft:emerald", manual_category="misc")

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
