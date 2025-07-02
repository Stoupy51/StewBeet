
# Imports
from beet import Context

# Constants
GENERATION_PLUGINS = (
    "stewbeet.plugins.verify_definitions",
    "stewbeet.plugins.resource_pack.sounds",
    "stewbeet.plugins.resource_pack.item_models",
    "stewbeet.plugins.resource_pack.check_power_of_2",
    "stewbeet.plugins.custom_recipes",
    "stewbeet.plugins.ingame_manual",
    "stewbeet.plugins.datapack.loading",
    "stewbeet.plugins.datapack.custom_blocks",
    "stewbeet.plugins.datapack.loot_tables",
    "stewbeet.plugins.compatibilities.simpledrawer",
    "stewbeet.plugins.compatibilities.neo_enchant"
)
FINALYZE_PLUGINS = (
    "stewbeet.plugins.finalyze.custom_blocks_ticking",
    "stewbeet.plugins.finalyze.basic_datapack_structure",
    "stewbeet.plugins.finalyze.dependencies",
    "stewbeet.plugins.finalyze.check_unused_textures",
    "stewbeet.plugins.finalyze.last_final",
    "stewbeet.plugins.auto.headers",
    "stewbeet.plugins.archive",
    "stewbeet.plugins.merge_smithed_weld",
    "stewbeet.plugins.copy_to_destination",
    "stewbeet.plugins.compute_sha1"
)

def beet_default(ctx: Context):
    """ Run all plugins that should run after definitions are loaded.
    This function will yield before finalizing the project (so users can run their own plugins in the middle of the pipeline).

    Requires:
        - StewBeet to be initialized (e.g. from stewbeet.plugins.initialize).
        - Definitions to be loaded
    """
    # Assertions
    for x in GENERATION_PLUGINS:
        ctx.require(x)

    # Yield to allow user code to run
    yield

    # After user code, run the final plugins
    for x in FINALYZE_PLUGINS:
        ctx.require(x)

