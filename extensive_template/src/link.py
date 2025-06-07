
# Imports
from beet import Context
from beet.core.utils import JsonDict
from stewbeet import core
from stewbeet.core.utils.io import *


# Main entry point (ran just before making finalyzing the build process (zip, headers, lang, ...))
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    database: JsonDict = core.Mem.database  # noqa: F841

    # Generate ores in the world
    core.CustomOreGeneration.all_with_config(ore_configs = {
        "steel_ore": [
            core.CustomOreGeneration(
                dimensions = ["minecraft:overworld","stardust:cavern","some_other:dimension"],
                maximum_height = 50,
                minimum_height = 0,
                veins_per_region = 2,
                vein_size_logic = 0.4,
            )
        ],
        "deepslate_steel_ore": [
            core.CustomOreGeneration(
                dimensions = ["minecraft:overworld"],
                maximum_height = 0,
                veins_per_region = 2,
                vein_size_logic = 0.4,
            ),
            core.CustomOreGeneration(
                dimensions = ["stardust:cavern"],
                maximum_height = 0,
                veins_per_region = 8,
                vein_size_logic = 0.8,
            )
        ],
    })


    # Add some commands when loading datapack
    write_load_file("""
# Add a message when loading
say Here is a message when loading the datapack, located in `src/link.py`
""")
    #	write_function("v{version}/load/confirm_load", ...)	<- This is the same as the previous line


    ## Clock functions
    # When you write to the following files: "tick_2", "second", "second_5", "minute"... the tick function will automatically call them, ex:
    write_versioned_function("minute", f"execute if score #spam {ns}.data matches 1 run say This is a message every minute\n")
    write_versioned_function("second_5", f"execute if score #spam {ns}.data matches 1 run say This is a SPAM message every 5 seconds\n")
    write_versioned_function("tick_2", f"execute if score #spam {ns}.data matches 1 run say This is a SPAM message every 2 ticks\n")
    # The two following functions calls are equivalent:
    #	write_tick_file(config, ...)
    #	write_versioned_file(config, "tick", ...)

    # Create a random function
    write_function(f"{ns}:path/to/a/random/function/i/guess", "say Hello world!")

    # Call a bookshelf module (Every single module from https://docs.mcbookshelf.dev/en/latest/ is supported)
    write_function(f"{ns}:bookshelf/test", """
# Once
scoreboard players set $math.divide.x bs.in 9
scoreboard players set $math.divide.y bs.in 5
function #bs.math:divide
tellraw @a [{"text": "9 / 5 = ", "color": "dark_gray"},{"score":{"name":"$math.divide", "objective": "bs.out"}, "color": "gold"}]
""")

    pass

