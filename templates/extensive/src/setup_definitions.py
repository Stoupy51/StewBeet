
# Imports
from beet import Context
from stewbeet import *  # type: ignore

# Additional imports (specific to this project)
from .definitions.additions import main as main_additions
from .definitions.manual_customization import main as main_manual_customization
from .definitions.ores import main as main_ores


# Main entry point
def beet_default(ctx: Context):

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    # (src/definitions/ores.py)
    main_ores()

    # Generate custom disc records in definitions
    generate_custom_records("auto")

    # Run additional definitions modifications (src/definitions/additions.py)
    # TODO: If you need to add items, you probably want to add them in src/definitions/additions.py, not here, to keep things organized.
    main_additions()

    # Add item categories to the remaining items (should select 'shazinho', 'super_stone', and 'stewbeet_painting' here)
    for item in Mem.definitions.keys():
        obj = Item.from_id(item)
        if not obj.manual_category:
            obj.manual_category = "miscellaneous"

    # Final adjustments, you definitively should keep them!
    add_item_model_component(black_list=["item_ids","you_don't_want","in_that","list"])
    add_item_name_and_lore_if_missing()
    add_private_custom_data_for_namespace()		# Add a custom namespace for easy item detection
    add_smithed_ignore_vanilla_behaviours_convention()	# Smithed items convention
    set_manual_components(white_list=["item_name", "lore", "custom_name", "damage", "max_damage"]) # Components to include in the manual when hovering items (here is the default list)

    # Customize the in-game manual using the ingame_manual_v2 API (custom pages, hooks, button layout)
    main_manual_customization()

    # Debug purposes: export all definitions to a single json file
    export_all_definitions_to_json(f"{Mem.ctx.directory}/definitions_debug.json")

