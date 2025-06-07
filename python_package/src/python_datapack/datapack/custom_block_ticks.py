
# Imports
from ..utils.io import FILES_TO_WRITE, write_file, write_function


def custom_blocks_ticks_and_second_functions(config: dict) -> None:
	""" Setup custom blocks ticks and second functions calls

	It will seek for "second.mcfunction" and "tick.mcfunction" files in the custom_blocks folder

	Then it will generate all functions to lead to the execution of these files by adding tags

	Args:
		config (dict): The config dictionary
	"""
	namespace: str = config['namespace']
	build_datapack: str = config['build_datapack']
	functions: str = f"{build_datapack}/data/{namespace}/function"
	custom_blocks = f"{functions}/custom_blocks"
	
	# Get second and ticks functions
	custom_blocks_second = []
	custom_blocks_tick = []
	for path in FILES_TO_WRITE:
		if custom_blocks in path:
			custom_block = path.split(custom_blocks + "/")[1]
			if custom_block.count("/") == 1:
				splitted = custom_block.split("/")
				function_name = splitted[1].replace(".mcfunction", "")
				custom_block = splitted[0]
				if function_name == "second":
					custom_blocks_second.append(custom_block)
				elif function_name == "tick":
					custom_blocks_tick.append(custom_block)
	
	# For each custom block, add tags when placed
	for custom_block in custom_blocks_second:
		write_file(f"{custom_blocks}/{custom_block}/place_secondary.mcfunction", f"\n# Add tag for loop every second\ntag @s add {namespace}.second\nscoreboard players add #second_entities {namespace}.data 1\n")
		write_file(f"{custom_blocks}/{custom_block}/destroy.mcfunction", f"\n# Decrease the number of entities with second tag\nscoreboard players remove #second_entities {namespace}.data 1\n")
	for custom_block in custom_blocks_tick:
		write_file(f"{custom_blocks}/{custom_block}/place_secondary.mcfunction", f"\n# Add tag for loop every tick\ntag @s add {namespace}.tick\nscoreboard players add #tick_entities {namespace}.data 1\n")
		write_file(f"{custom_blocks}/{custom_block}/destroy.mcfunction", f"\n# Decrease the number of entities with tick tag\nscoreboard players remove #tick_entities {namespace}.data 1\n")
	
	# Write second functions
	version: str = config['version']
	if custom_blocks_second:
		score_check: str = f"score #second_entities {namespace}.data matches 1.."
		write_file(f"{functions}/v{version}/second.mcfunction", f"\n# Custom blocks second functions\nexecute if {score_check} as @e[tag={namespace}.second] at @s run function {namespace}:custom_blocks/second")
		content = "\n".join(f"execute if entity @s[tag={namespace}.{custom_block}] run function {namespace}:custom_blocks/{custom_block}/second" for custom_block in custom_blocks_second)
		write_file(f"{custom_blocks}/second.mcfunction", content)

		# Write in stats_custom_blocks
		write_function(config, f"{namespace}:_stats_custom_blocks",f'scoreboard players add #second_entities {namespace}.data 0\n', prepend = True)
		write_function(config, f"{namespace}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- \'second\' tag function: ","color":"green"}},{{"score":{{"name":"#second_entities","objective":"{namespace}.data"}},"color":"dark_green"}}]\n'
		)

	
	# Write tick functions
	if custom_blocks_tick:
		score_check: str = f"score #tick_entities {namespace}.data matches 1.."
		write_file(f"{functions}/v{version}/tick.mcfunction", f"\n# Custom blocks tick functions\nexecute if {score_check} as @e[tag={namespace}.tick] at @s run function {namespace}:custom_blocks/tick")
		content = "\n".join(f"execute if entity @s[tag={namespace}.{custom_block}] run function {namespace}:custom_blocks/{custom_block}/tick" for custom_block in custom_blocks_tick)
		write_file(f"{custom_blocks}/tick.mcfunction", content)

		# Write in stats_custom_blocks
		write_function(config, f"{namespace}:_stats_custom_blocks",f'scoreboard players add #tick_entities {namespace}.data 0\n', prepend = True)
		write_function(config, f"{namespace}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- \'tick\' tag function: ","color":"green"}},{{"score":{{"name":"#tick_entities","objective":"{namespace}.data"}},"color":"dark_green"}}]\n'
		)

