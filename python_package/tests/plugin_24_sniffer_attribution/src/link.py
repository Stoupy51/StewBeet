# User code extending what custom_blocks generated, the supported way.
# .obj.append reaches beet directly without passing through write_function, so this line is mapped
# only because beet.Function.append is patched by the sniffer plugin.

# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    Block.from_id("attributed_block").functions.place_secondary.obj.append("say appended by the author")

