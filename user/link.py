
# Imports
from python_datapack.utils.database_helper import *

# Main function is run just before making finalyzing the build process (zip, headers, lang, ...)
def main(config: dict) -> None:
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

	pass

