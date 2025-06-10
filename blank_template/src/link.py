
# Imports
from beet import Context
from beet.core.utils import JsonDict
from stewbeet import core
from stewbeet.core.utils.io import *


# Main entry point (ran just before making finalyzing the build process (zip, headers, lang, ...))
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    definitions: JsonDict = core.Mem.definitions  # noqa: F841

    # Generate ores in the world
    # See extensive_template/src/link.py for an example

    # You can either write your mcfunction files in src/data/... or with the python way:
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
    write_function(f"{ns}:path/to/a/random/function/i/guess", """tellraw @a {"text":"Hello world!"}""")

    # See more examples in extensive_template/src/link.py

    pass

