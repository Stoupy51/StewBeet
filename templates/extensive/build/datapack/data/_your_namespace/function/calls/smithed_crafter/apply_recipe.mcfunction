
#> _your_namespace:calls/smithed_crafter/apply_recipe
#
# @within	_your_namespace:calls/smithed_crafter/shapeless_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_ingot_x9"}
#			_your_namespace:calls/smithed_crafter/shapeless_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_nugget_x9"}
#			_your_namespace:calls/smithed_crafter/shapeless_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/raw_steel_x9"}
#			_your_namespace:calls/smithed_crafter/shapeless_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/super_stone"}
#			_your_namespace:calls/smithed_crafter/shapeless_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/manual"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_ingot"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_stick_x4"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_block"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/raw_steel_block"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_helmet"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_chestplate"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_leggings"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_boots"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_sword"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_pickaxe"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_axe"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_shovel"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/steel_hoe"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/stone_stick_x4"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/stone_rod"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/super_stone"}
#			_your_namespace:calls/smithed_crafter/shaped_recipes {command: "loot replace block ~ ~ ~ container.16 loot _your_namespace:i/stewbeet_painting"}
#
# @args		command (string)
#

# Set the consume_tools flag
data modify storage smithed.crafter:input flags set value ["consume_tools"]

# Perform the loot command
$return run $(command)

