
# Imports
from beet import Context
from stouputils.decorators import measure_time
from stouputils.print import progress

from ....core.__memory__ import Mem
from ....core.utils.io import write_function, write_versioned_function


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking'")
def beet_default(ctx: Context):
	""" Main entry point for the custom blocks ticking plugin.
	This plugin sets up custom blocks ticks and second functions calls.

	It will seek for "second.mcfunction" and "tick.mcfunction" files in the custom_blocks folder
	Then it will generate all functions to lead to the execution of these files by adding tags.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None:
		Mem.ctx = ctx

	# Get namespace
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# Get second and ticks functions from the context
	custom_blocks_second: list[str] = []
	custom_blocks_tick: list[str] = []

	# Check for custom block functions in the data pack
	for function_path in ctx.data.functions:
		if function_path.startswith(f"{ns}:custom_blocks/") and "/" in function_path[len(f"{ns}:custom_blocks/"):]:

			# Split the path to get custom block name and function type
			parts = function_path[len(f"{ns}:custom_blocks/"):].split("/")
			if len(parts) == 2:
				custom_block, function_name = parts
				if function_name == "second":
					custom_blocks_second.append(custom_block)
				elif function_name == "tick":
					custom_blocks_tick.append(custom_block)

	# For each custom block, add tags when placed
	for custom_block in custom_blocks_second:
		write_function(f"{ns}:custom_blocks/{custom_block}/place_secondary",
			f"# Add tag for loop every second\ntag @s add {ns}.second\nscoreboard players add #second_entities {ns}.data 1\n")
		write_function(f"{ns}:custom_blocks/{custom_block}/destroy",
			f"# Decrease the number of entities with second tag\nscoreboard players remove #second_entities {ns}.data 1\n")

	for custom_block in custom_blocks_tick:
		write_function(f"{ns}:custom_blocks/{custom_block}/place_secondary",
			f"# Add tag for loop every tick\ntag @s add {ns}.tick\nscoreboard players add #tick_entities {ns}.data 1\n")
		write_function(f"{ns}:custom_blocks/{custom_block}/destroy",
			f"# Decrease the number of entities with tick tag\nscoreboard players remove #tick_entities {ns}.data 1\n")

	# Write second functions
	if custom_blocks_second:
		score_check: str = f"score #second_entities {ns}.data matches 1.."
		write_versioned_function("second",
			f"# Custom blocks second functions\nexecute if {score_check} as @e[tag={ns}.second] at @s run function {ns}:custom_blocks/second")

		content = "\n".join(
			f"execute if entity @s[tag={ns}.{custom_block}] run function {ns}:custom_blocks/{custom_block}/second"
			for custom_block in custom_blocks_second
		)
		write_function(f"{ns}:custom_blocks/second", content)

		# Write in stats_custom_blocks
		write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #second_entities {ns}.data 0', prepend=True)
		write_function(f"{ns}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- \'second\' tag function: ","color":"green"}},{{"score":{{"name":"#second_entities","objective":"{ns}.data"}},"color":"dark_green"}}]')

	# Write tick functions
	if custom_blocks_tick:
		score_check: str = f"score #tick_entities {ns}.data matches 1.."
		write_versioned_function("tick", f"# Custom blocks tick functions\nexecute if {score_check} as @e[tag={ns}.tick] at @s run function {ns}:custom_blocks/tick")

		content = "\n".join(
			f"execute if entity @s[tag={ns}.{custom_block}] run function {ns}:custom_blocks/{custom_block}/tick"
			for custom_block in custom_blocks_tick
		)
		write_function(f"{ns}:custom_blocks/tick", content)

		# Write in stats_custom_blocks
		write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #tick_entities {ns}.data 0', prepend=True)
		write_function(f"{ns}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- \'tick\' tag function: ","color":"green"}},{{"score":{{"name":"#tick_entities","objective":"{ns}.data"}},"color":"dark_green"}}]')

