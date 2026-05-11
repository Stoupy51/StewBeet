
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):

    # Auto-discover all .ogg files in the records_folder and create jukebox songs
    generate_custom_records("auto", category="music")

    # Final adjustments
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()
