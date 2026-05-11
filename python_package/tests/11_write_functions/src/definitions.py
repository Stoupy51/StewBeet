
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # No items needed for this test; write_functions are added in src/link.py
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
