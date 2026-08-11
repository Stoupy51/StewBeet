
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

    # A 512x512 source displayed 32 pixels tall: too big for one glyph, so it becomes a 2x2 grid of
    # them put back together with negative spacing. The ascent is explicit so the rows cut exactly
    # on the quadrants of the source.
    write_function(f"{ctx.project_id}:big", """
tellraw @a ["Logo: ",{"render":"big_logo","height":32,"ascent":16}]
""")

    # An ascent above the height floats the glyph over the baseline, which Minecraft only accepts
    # when the texture reaches down to it: the image is padded rather than the ascent lowered.
    write_function(f"{ctx.project_id}:floating", """
tellraw @a ["Up: ",{"render":"steel_ingot","height":8,"ascent":20}]
""")
