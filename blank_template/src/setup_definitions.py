
# ruff: noqa: F841
# Imports
from beet import Context
from stewbeet import core
from stewbeet.core import Mem

# Configuration to generate everything about a material
ORES_CONFIGS: dict[str, core.EquipmentsConfig|None] = {
    # See extensive_template/src/setup_definitions.py for an example
}

# Main entry point
def beet_default(ctx: Context):
    if Mem.ctx is None:
        Mem.ctx = ctx
    ns: str = ctx.project_id    # Namespace of the project, use it as you please.

    # Generate ores in definitions (add every stuff (found in the textures folder) related to the given materials, to the definitions)
    core.generate_everything_about_these_materials(ORES_CONFIGS)

    # Add items to the definitions
    # See extensive_template/src/setup_definitions.py for examples

    # Final adjustments, you definitively should keep them!
    core.add_item_model_component(black_list = ["item_ids","you_don't_want","in_that","list"])
    core.add_item_name_and_lore_if_missing()
    core.add_private_custom_data_for_namespace()		# Add a custom namespace for easy item detection
    core.add_smithed_ignore_vanilla_behaviours_convention()	# Smithed items convention

