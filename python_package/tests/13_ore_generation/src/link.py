
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point (runs after all definition plugins)
def beet_default(ctx: Context):

    # Generate ore veins in multiple dimensions
    CustomOreGeneration.all_with_config(ore_configs={
        "test_ore": [
            # Overworld: medium frequency, near surface
            CustomOreGeneration(
                dimensions=["minecraft:overworld"],
                maximum_height=50,
                minimum_height=0,
                veins_per_region=1.2,
                vein_size_logic=0.4,
            ),
            # Nether: different settings
            CustomOreGeneration(
                dimensions=["minecraft:the_nether"],
                maximum_height=100,
                minimum_height=20,
                veins_per_region=0.8,
                vein_size_logic=0.3,
            ),
        ],
        "deepslate_test_ore": [
            # Overworld deep only
            CustomOreGeneration(
                dimensions=["minecraft:overworld"],
                maximum_height=0,
                veins_per_region=1.2,
                vein_size_logic=0.4,
            ),
            # Custom dimension
            CustomOreGeneration(
                dimensions=["test_ns:custom_dimension", "minecraft:overworld"],
                maximum_height=0,
                veins_per_region=3.6,
                vein_size_logic=0.8,
            ),
        ],
    })
