
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version

    # Write timer functions so that basic_datapack_structure detects them
    write_versioned_function("tick_2", f"say every 2 ticks ({ns})")
    write_versioned_function("second", f"say every second ({ns})")
