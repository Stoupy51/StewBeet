
# Imports
import stouputils as stp
from beet import Context

from ....core.__memory__ import Mem
from ....core.utils.io import write_function, write_versioned_function


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking'")
def beet_default(ctx: Context):
	""" Main entry point for the custom blocks ticking plugin.
	This plugin sets up custom blocks ticks and second functions calls.

	It will seek for "second.mcfunction", "tick.mcfunction", and more files in the custom_blocks folder
	Then it will generate all functions to lead to the execution of these files by adding tags.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# Get namespace
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# Get ticks functions from the context
	for ticking in ["tick", "tick_2", "second", "second_5", "minute"]:
		custom_blocks_tick: list[str] = []

		# Check for custom block functions in the data pack
		for function_path in ctx.data.functions:
			if function_path.startswith(f"{ns}:custom_blocks/") and "/" in function_path[len(f"{ns}:custom_blocks/"):]:

				# Split the path to get custom block name and function type
				parts = function_path[len(f"{ns}:custom_blocks/"):].split("/")
				if len(parts) == 2:
					custom_block, function_name = parts
					if function_name == ticking:
						custom_blocks_tick.append(custom_block)

		# For each custom block, add tags when placed
		for custom_block in custom_blocks_tick:
			write_function(f"{ns}:custom_blocks/{custom_block}/place_secondary",
				f"# Add tag for loop every {ticking}\ntag @s add {ns}.{ticking}\nscoreboard players add #{ticking}_entities {ns}.data 1\n")
			write_function(f"{ns}:custom_blocks/{custom_block}/destroy",
				f"# Decrease the number of entities with {ticking} tag\nscoreboard players remove #{ticking}_entities {ns}.data 1\n")

		# Write ticking functions
		if custom_blocks_tick:
			score_check: str = f"score #{ticking}_entities {ns}.data matches 1.."
			write_versioned_function(ticking, f"# Custom blocks {ticking} functions\nexecute if {score_check} as @e[tag={ns}.{ticking}] at @s run function {ns}:custom_blocks/{ticking}")

			content = "\n".join(
				f"execute if entity @s[tag={ns}.{custom_block}] run function {ns}:custom_blocks/{custom_block}/{ticking}"
				for custom_block in custom_blocks_tick
			)
			write_function(f"{ns}:custom_blocks/{ticking}", content)

			# Write in stats_custom_blocks
			write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #{ticking}_entities {ns}.data 0', prepend=True)
			write_function(f"{ns}:_stats_custom_blocks",
				f'tellraw @s [{{"text":"- \'{ticking}\' tag function: ","color":"green"}},{{"score":{{"name":"#{ticking}_entities","objective":"{ns}.data"}},"color":"dark_green"}}]')

