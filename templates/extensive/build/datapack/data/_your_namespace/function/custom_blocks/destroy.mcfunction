
#> _your_namespace:custom_blocks/destroy
#
# @executed	as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s
#
# @within	_your_namespace:v3.0.0/tick_2 [ as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s ]
#			_your_namespace:v3.0.0/second [ as @e[type=#_your_namespace:custom_blocks,tag=...,predicate=!_your_namespace:advanced_check_vanilla_blocks] & at @s ]
#			_your_namespace:v3.0.0/second_5 [ as @e[type=item_display,tag=_your_namespace.custom_block,predicate=!_your_namespace:advanced_check_vanilla_blocks] & at @s ]
#			_your_namespace:calls/common_signals/custom_block_destroy [ as @e[tag=_your_namespace.custom_block,dx=0,dy=0,dz=0] & at @s ]
#

# Check for missing vanilla blocks
execute if score #total_vanilla_cobblestone _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_cobblestone] unless block ~ ~ ~ minecraft:cobblestone run return run function _your_namespace:custom_blocks/_groups/minecraft_cobblestone
execute if score #total_vanilla_iron_block _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_iron_block] unless block ~ ~ ~ minecraft:iron_block run return run function _your_namespace:custom_blocks/_groups/minecraft_iron_block
execute if score #total_vanilla_polished_deepslate _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_polished_deepslate] unless block ~ ~ ~ minecraft:polished_deepslate run return run function _your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
execute if score #total_vanilla_raw_iron_block _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_raw_iron_block] unless block ~ ~ ~ minecraft:raw_iron_block run return run function _your_namespace:custom_blocks/_groups/minecraft_raw_iron_block

