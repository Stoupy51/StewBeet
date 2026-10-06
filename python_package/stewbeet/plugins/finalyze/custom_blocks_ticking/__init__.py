
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, Function

from ....core.__memory__ import Mem
from ....core.cls.block_functions import BlockFunctions
from ....core.cls.resource import Resource
from ....core.constants import CUSTOM_BLOCKS_FOLDER
from ....core.utils.io import write_function, write_versioned_function


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.custom_blocks_ticking'")
def beet_default(ctx: Context):
	""" Main entry point for the custom blocks ticking plugin.
	This plugin sets up custom blocks ticks and second functions calls.

	It will seek for "second.mcfunction", "tick.mcfunction", and more files in the custom_blocks folder
	Then it will generate all functions to lead to the execution of these files by adding tags.

	Args:
		ctx: The beet context.
	"""
	# Get namespace
	Mem.ctx = ctx
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# Prefix shared with the writers, so renaming the folder can't silently break discovery
	custom_blocks_prefix: str = f"{Resource(Function, CUSTOM_BLOCKS_FOLDER)}/"

	for ticking in ["tick", "tick_2", "second", "second_5", "minute"]:
		custom_blocks_tick: list[str] = blocks_with_function(custom_blocks_prefix, ticking)
		if custom_blocks_tick:
			write_ticking(ns, ticking, custom_blocks_tick)


def blocks_with_function(custom_blocks_prefix: str, ticking: str) -> list[str]:
	""" The custom blocks that have a function of this name, `<custom blocks folder>/<block>/<ticking>`. """
	blocks: list[str] = []
	for function_path in Mem.ctx.data.functions:
		parts: list[str] = function_path[len(custom_blocks_prefix):].split("/")
		if function_path.startswith(custom_blocks_prefix) and len(parts) == 2 and parts[1] == ticking:
			blocks.append(parts[0])
	return blocks


def write_ticking(ns: str, ticking: str, custom_blocks_tick: list[str]) -> None:
	""" Tag each custom block running a function every `ticking` when placed, and dispatch to them from the `ticking` function. """
	for custom_block in custom_blocks_tick:
		functions: BlockFunctions = BlockFunctions(custom_block)
		write_function(functions.place_secondary,
			f"# Add tag for loop every {ticking}\ntag @s add {ns}.{ticking}\n"
			f"scoreboard players add #{ticking}_entities {ns}.data 1\n")
		write_function(functions.destroy,
			f"# Decrease the number of entities with {ticking} tag\nscoreboard players remove #{ticking}_entities {ns}.data 1\n")

	score_check: str = f"score #{ticking}_entities {ns}.data matches 1.."
	dispatcher: Resource[Function] = Resource(Function, f"{CUSTOM_BLOCKS_FOLDER}/{ticking}")
	write_versioned_function(
		ticking,
		f"# Custom blocks {ticking} functions\n"
		f"execute if {score_check} as @e[tag={ns}.{ticking}] at @s run function {dispatcher}",
	)

	content = "\n".join(
		f"execute if entity @s[tag={ns}.{custom_block}] run function {BlockFunctions(custom_block)[ticking]}"
		for custom_block in custom_blocks_tick
	)
	write_function(dispatcher, content)

	# Write in stats_custom_blocks
	write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #{ticking}_entities {ns}.data 0', prepend=True)
	write_function(f"{ns}:_stats_custom_blocks",
		f'tellraw @s [{{"text":"- \'{ticking}\' tag function: ","color":"green"}},'
		f'{{"score":{{"name":"#{ticking}_entities","objective":"{ns}.data"}},"color":"dark_green"}}]')

