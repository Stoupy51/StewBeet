# What simple_item_plugin does to the load function of every project using it.

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context) -> None:
	ctx.data.functions["tns:load"].prepend("scoreboard objectives add tns.math dummy")

