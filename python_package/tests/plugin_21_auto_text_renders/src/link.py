
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    # A render inside a command: the same (id, height, ascent) as the lore one, so it must reuse its glyph
    write_function(f"{ctx.project_id}:show", """
tellraw @a ["Look: ",{"render":"steel_ingot","height":8},{"render":"minecraft:stone","color":"red"}]
""")

    # A render nested in a hover_event, and a decoy "height" belonging to a sub-object
    write_function(f"{ctx.project_id}:hover", """
tellraw @a {"render":"steel_ingot","hover_event":{"action":"show_text","value":{"text":"a","height":99}}}
""")
