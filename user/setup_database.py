
# Import database helper
from python_datapack.utils.database_helper import *

# Constants
STARTING_CMD: int = 30000	# Prefix for custom_model_data


# Configuration to generate everything about the material based on "super_iron_ingot"
ORES_CONFIGS: dict[str, EquipmentsConfig|None] = {
	"super_iron_ingot":	EquipmentsConfig(
		# This super iron is equivalent to iron,
		equivalent_to = DEFAULT_ORE.IRON,

		# But, has more durability (3 times more)
		pickaxe_durability = 3 * VanillaEquipments.PICKAXE.value[DEFAULT_ORE.IRON]["durability"],

		# And, does 1 more damage per hit, and has 0.5 more armor, and mines 20% faster
		attributes = {"generic.attack_damage": 1, "generic.armor": 0.5, "player.mining_efficiency": 0.2}
	),
}

# Main function should return a database
def main(config: dict) -> dict[str, dict]:
	database = {}

	# Generate ores in database
	generate_everything_about_these_ores(config, database, ORES_CONFIGS)
	# TODO: add world geenration ore

	# Generate custom disc records
	generate_custom_records(config, database, "auto")

	# Add a super stone block that can be crafted with 9 deepslate or stone, and is equivalent to stone
	database["super_stone"] = {
		"id": CUSTOM_BLOCK_VANILLA, VANILLA_BLOCK: {"id": "minecraft:stone", "apply_facing": False},
		RESULT_OF_CRAFTING: [
			{"type":"crafting_shaped","result_count":1,"group":"super_stone","category":"blocks","shape":["XXX","XXX","XXX"],"ingredients": {"X": ingr_repr("minecraft:stone")}},
			{"type":"crafting_shapeless","result_count":1,"group":"super_stone","category":"blocks","ingredients":[ingr_repr("minecraft:deepslate")]*9 },
		],
	}

	# Don't forget to add the vanilla blocks for the custom blocks
	database["super_iron_block"][VANILLA_BLOCK] = {"id": "minecraft:iron_block", "apply_facing": False}
	database["super_iron_ore"][VANILLA_BLOCK] = {"id": "minecraft:iron_ore", "apply_facing": False}
	database["deepslate_super_iron_ore"][VANILLA_BLOCK] = {"id": "minecraft:deepslate_iron_ore", "apply_facing": False}
	database["raw_super_iron_block"][VANILLA_BLOCK] = {"id": "minecraft:raw_iron_block", "apply_facing": False}

	# Final adjustments
	deterministic_custom_model_data(config, database, STARTING_CMD, black_list = ["item_names","you_don't_want","in_that","list"])
	add_item_name_and_lore_if_missing(config, database)
	add_private_custom_data_for_namespace(config, database)
	add_smithed_ignore_vanilla_behaviours_convention(database)
	print()

	# Return database
	return database

