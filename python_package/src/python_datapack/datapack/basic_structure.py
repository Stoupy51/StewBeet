
# Imports
from ..utils.io import is_in_write_queue, write_tick_file, write_versioned_function


def main(config: dict):
	version: str = config['version']
	namespace: str = config['namespace']
	functions: str = f"{config['build_datapack']}/data/{namespace}/function/v{version}"
	tick_2: str = f"{functions}/tick_2.mcfunction"
	second: str = f"{functions}/second.mcfunction"
	second_5: str = f"{functions}/second_5.mcfunction"
	minute: str = f"{functions}/minute.mcfunction"

	# Prepend to tick_2, second, second_5, and minute if they exists
	if is_in_write_queue(tick_2):
		write_versioned_function(config, "tick_2",
f"""
# Reset timer
scoreboard players set #tick_2 {namespace}.data 1
""", prepend = True)
	if is_in_write_queue(second):
		write_versioned_function(config, "second",
f"""
# Reset timer
scoreboard players set #second {namespace}.data 0
""", prepend = True)
	if is_in_write_queue(second_5):
		write_versioned_function(config, "second_5",
f"""
# Reset timer
scoreboard players set #second_5 {namespace}.data -10
""", prepend = True)
	if is_in_write_queue(minute):
		write_versioned_function(config, "minute",
f"""
# Reset timer
scoreboard players set #minute {namespace}.data 1
""", prepend = True)

	# Tick structure, tick_2 and second_5 are "offsync" for a better load distribution
	if is_in_write_queue(tick_2) or is_in_write_queue(second) or is_in_write_queue(second_5) or is_in_write_queue(minute):
		content: str = "# Timers\n"
		if is_in_write_queue(tick_2):
			content += f"scoreboard players add #tick_2 {namespace}.data 1\n"
		if is_in_write_queue(second):
			content += f"scoreboard players add #second {namespace}.data 1\n"
		if is_in_write_queue(second_5):
			content += f"scoreboard players add #second_5 {namespace}.data 1\n"
		if is_in_write_queue(minute):
			content += f"scoreboard players add #minute {namespace}.data 1\n"

		if is_in_write_queue(tick_2):
			content += f"execute if score #tick_2 {namespace}.data matches 3.. run function {namespace}:v{version}/tick_2\n"
		if is_in_write_queue(second):
			content += f"execute if score #second {namespace}.data matches 20.. run function {namespace}:v{version}/second\n"
		if is_in_write_queue(second_5):
			content += f"execute if score #second_5 {namespace}.data matches 90.. run function {namespace}:v{version}/second_5\n"
		if is_in_write_queue(minute):
			content += f"execute if score #minute {namespace}.data matches 1200.. run function {namespace}:v{version}/minute\n"
		if content:
			write_tick_file(config, content, prepend = True)


