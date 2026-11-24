# Imports
from beet import Context

from stewbeet import BlockFunctions, write_function
from stewbeet.contrib.simplenergy import keep_energy_for_batteries, setup_wrench


# Main entry point
def beet_default(ctx: Context):
	ns: str = ctx.project_id

	# The SimplEnergy hooks on an interaction block, whose host never drops an item nor lets the tool in hand be used
	keep_energy_for_batteries(["bf_lamp"])
	setup_wrench("all")

	# Clicks counted where a test reads them
	write_function(BlockFunctions("bf_lamp").right_click, f"scoreboard players add #right_clicks {ns}.data 1")
	write_function(BlockFunctions("bf_lamp").left_click, f"scoreboard players add #left_clicks {ns}.data 1")

