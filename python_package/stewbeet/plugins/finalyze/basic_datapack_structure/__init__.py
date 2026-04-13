
# Imports
from typing import Callable, Literal
from re import Match, Pattern, compile

import stouputils as stp
from beet import Context

from ....core.__memory__ import Mem
from ....core.utils.io import write_tick_file, write_versioned_function, write_unload_file


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.basic_datapack_structure'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the basic datapack structure plugin.
	This plugin sets up basic timing structures for a Minecraft datapack with tick functions
	for different intervals (tick_2, second, second_5, minute).

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# Get namespace and version
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id
	version: str = ctx.project_version

	create_timer_structure(ctx, ns, version)
	UnloadFunction(ctx, ns, version)

def create_timer_structure(ctx: Context, ns: str, version: str) -> None:
	# Define function paths
	tick_2_path: str = f"{ns}:v{version}/tick_2"
	second_path: str = f"{ns}:v{version}/second"
	second_5_path: str = f"{ns}:v{version}/second_5"
	minute_path: str = f"{ns}:v{version}/minute"

	# Check if functions exist in the data pack
	tick_2_exists: bool = tick_2_path in ctx.data.functions
	second_exists: bool = second_path in ctx.data.functions
	second_5_exists: bool = second_5_path in ctx.data.functions
	minute_exists: bool = minute_path in ctx.data.functions

	# Prepend timer reset to existing functions
	if tick_2_exists:
		write_versioned_function("tick_2",
f"""# Reset timer
scoreboard players set #tick_2 {ns}.data 1
""", prepend=True)

	if second_exists:
		write_versioned_function("second",
f"""# Reset timer
scoreboard players set #second {ns}.data 0
""", prepend=True)

	if second_5_exists:
		write_versioned_function("second_5",
f"""# Reset timer
scoreboard players set #second_5 {ns}.data -10
""", prepend=True)

	if minute_exists:
		write_versioned_function("minute",
f"""# Reset timer
scoreboard players set #minute {ns}.data 1
""", prepend=True)
	# Generate tick structure if any timer functions exist
	if tick_2_exists or second_exists or second_5_exists or minute_exists:
		content: str = "# Timers\n"

		# Add scoreboard increments for existing timers
		if tick_2_exists:
			content += f"scoreboard players add #tick_2 {ns}.data 1\n"
		if second_exists:
			content += f"scoreboard players add #second {ns}.data 1\n"
		if second_5_exists:
			content += f"scoreboard players add #second_5 {ns}.data 1\n"
		if minute_exists:
			content += f"scoreboard players add #minute {ns}.data 1\n"

		# Add function calls when timers reach their thresholds
		# tick_2 and second_5 are "offsync" for better load distribution
		if tick_2_exists:
			content += f"execute if score #tick_2 {ns}.data matches 3.. run function {ns}:v{version}/tick_2\n"
		if second_exists:
			content += f"execute if score #second {ns}.data matches 20.. run function {ns}:v{version}/second\n"
		if second_5_exists:
			content += f"execute if score #second_5 {ns}.data matches 90.. run function {ns}:v{version}/second_5\n"
		if minute_exists:
			content += f"execute if score #minute {ns}.data matches 1200.. run function {ns}:v{version}/minute\n"

		# Write the timer logic to the tick file
		if content:
			write_tick_file(content, prepend=True)

type UnloadFunctionKeys = Literal["items", "scoreboard_objectives", "storages"]

class UnloadFunction:
	""" Class to generate the unload functions for the datapack """

	def __init__(self, ctx: Context, ns: str, version: str) -> None:
		self.ctx = ctx
		self.ns = ns
		self.version = version

		self.removal_commands: dict[UnloadFunctionKeys, tuple[str,set[str]]] = {
			"items": (
				"# Clear custom items",
				{
					'clear @a *[custom_data~{"%s":{}}]' % self.ns,
				}
			),
			"scoreboard_objectives": (
				"# Remove scoreboard objectives",
				set()
			),
			"storages": (
				"# Clear storages",
				set()
			),
		}

		self.scan_datapack(ns)
		self.write_unload_function()

	def scan_datapack(self, ns: str) -> None:
		regexes: dict[UnloadFunctionKeys, tuple[Pattern[str], Callable[[Match[str]], str]]] = {
			"scoreboard_objectives": (
				compile(rf"scoreboard objectives add ([^ ]+)"),
				lambda match: f"scoreboard objectives remove {match.group(1)}"
			),
			"storages": (
				compile(rf"data modify storage ({ns}:\w+) (\w+)"),
				lambda match: f"data remove storage {match.group(1)} {match.group(2)}"
			),
		}

		for func in self.ctx.data.functions.values():
			for line in func.text.splitlines():
				for key, (regex, callback) in regexes.items():
					match = regex.search(line)
					if match:
						self.removal_commands[key][1].add(callback(match))

	def write_unload_function(self) -> None:
		content = "\n\n".join(
			f"{header}\n{'\n'.join(commands)}"
			for _, (header, commands) in self.removal_commands.items()
			if len(commands) > 0
		)
		write_unload_file(content)
