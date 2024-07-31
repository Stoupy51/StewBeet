
# Imports
from python_datapack.utils.database_helper import *

# Main function is run just before making finalyzing the build process (zip, headers, lang, ...)
def main(config: dict) -> None:

	# Get the namespace and database (if needed, actually not needed here)
	database: dict[str, dict] = config["database"]
	namespace: str = config["namespace"]

	# Generate ores in the world
	CustomOreGeneration.all_with_config(config, ore_configs = {
		"super_iron_ore": [
			CustomOreGeneration(
				dimensions = ["minecraft:overworld","stardust:cavern","some_other:dimension"],
				maximum_height = 50,
				minimum_height = 0,
				veins_per_region = 2,
				vein_size_logic = 0.4,
			)
		],
		"deepslate_super_iron_ore": [
			CustomOreGeneration(
				dimensions = ["minecraft:overworld"],
				maximum_height = 0,
				veins_per_region = 2,
				vein_size_logic = 0.4,
			),
			CustomOreGeneration(
				dimensions = ["stardust:cavern"],
				maximum_height = 0,
				veins_per_region = 8,
				vein_size_logic = 0.8,
			)
		],
	})


	# Add some commands when loading datapack
	write_to_load_file(config, f"""
# Add a message when loading
say Here is a message when loading the datapack, located in `user/link.py`
""")
	#	write_to_versioned_file(config, "load/confirm_load", ...)	<- This is the same as the previous line
	

	## Clock functions
	# When you write to the following files: "tick_2", "second", "second_5", "minute"... the tick function will automatically call them, ex:
	write_to_versioned_file(config, "minute", "say This is a message every minute\n")
	write_to_versioned_file(config, "second_5", "say This is a message every 5 seconds\n")
	write_to_versioned_file(config, "tick_2", "say This is a message every 2 ticks\n")
	# The two following functions calls are equivalent:
	#	write_to_tick_file(config, ...)
	#	write_to_versioned_file(config, "tick", ...)

	pass

