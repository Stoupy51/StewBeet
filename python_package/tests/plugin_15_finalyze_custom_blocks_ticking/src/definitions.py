
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # Custom block with a tick function and a second function
    Block(
        id="ticking_block",
        manual_category="misc",
        vanilla_block=VanillaBlock(id="minecraft:cobblestone"),
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
    add_smithed_ignore_vanilla_behaviours_convention()
