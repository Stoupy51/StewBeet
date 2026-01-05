
# Imports
from beet import Context
from stewbeet import *

# Additional imports (specific to this project)
from .definitions.additions import main as main_additions
from .definitions.ores import main as main_ores


# Main entry point
def beet_default(ctx: Context):

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    # (src/definitions/ores.py)
    main_ores()

    # Generate custom disc records in definitions
    generate_custom_records("auto")

    # Run additional definitions modifications (src/definitions/additions.py)
    main_additions()

    # Final adjustments, you definitively should keep them!
    add_item_model_component(black_list=["item_ids","you_don't_want","in_that","list"])
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()		# Add a custom namespace for easy item detection
    add_smithed_ignore_vanilla_behaviours_convention()	# Smithed items convention
    set_manual_components(white_list=["item_name", "lore", "custom_name", "damage", "max_damage"]) # Components to include in the manual when hovering items (here is the default list)

    # Debug purposes: export all definitions to a single json file
    export_all_definitions_to_json(f"{Mem.ctx.directory}/definitions_debug.json")

