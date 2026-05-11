
# Imports
from beet import Context
from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version

    # Write tick and second ticking functions for the custom block
    # custom_blocks_ticking detects these and enhances place_secondary + destroy
    write_function(f"{ns}:custom_blocks/ticking_block/tick", "say ticking_block tick")
    write_function(f"{ns}:custom_blocks/ticking_block/second", "say ticking_block second")
