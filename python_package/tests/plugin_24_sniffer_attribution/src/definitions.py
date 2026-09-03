# Declarations for: attribution scopes
# assertions.py finds the Block( line by reading this file, so moving the declaration is fine.

# Imports
from beet import Context

from stewbeet import Block, VanillaBlock


# Main entry point
def beet_default(ctx: Context) -> None:
    Block(
        id="attributed_block",
        manual_category="misc",
        vanilla_block=VanillaBlock(id="minecraft:furnace", block_facing="player"),
    )

