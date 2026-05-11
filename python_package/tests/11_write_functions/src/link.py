
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point (runs after all definition plugins)
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # write_function: write a named mcfunction file with arbitrary commands
    write_function(f"{ns}:utils/test_function", """
# This function is written by the write_function helper
say Hello from write_function!
""")

    # write_function: nested path
    write_function(f"{ns}:path/to/a/deep/function", """
# Deeply nested function
execute as @a run say deep function called
""")

    # write_load_file: append to the versioned load function
    write_load_file("""
# Message on load (written by write_load_file)
say Datapack loaded!
""")

    # write_versioned_function: append to named versioned sub-functions
    write_versioned_function("minute", f"execute if score #tick {ns}.data matches 0 run say One minute passed\n")
    write_versioned_function("second_5", f"execute if score #tick {ns}.data matches 0 run say Five seconds passed\n")
    write_versioned_function("tick_2", f"execute if score #tick {ns}.data matches 0 run say Two ticks passed\n")

    # write_tick_file: append to the tick function (equivalent to write_versioned_function("tick", ...))
    write_tick_file(f"# Called every tick\nexecute if score #counter {ns}.data matches 1 run say tick!\n")
