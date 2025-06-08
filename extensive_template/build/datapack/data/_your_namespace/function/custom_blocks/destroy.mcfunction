
#> _your_namespace:custom_blocks/destroy
#
# @within	_your_namespace:v2.0.0/tick_2
#			_your_namespace:v2.0.0/second
#			_your_namespace:v2.0.0/second_5
#			_your_namespace:calls/common_signals/on_ore_destroyed
#

execute if score #total_vanilla_cobblestone _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_cobblestone] unless block ~ ~ ~ minecraft:cobblestone run function _your_namespace:custom_blocks/_groups/minecraft_cobblestone
execute if score #total_vanilla_iron_block _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_iron_block] unless block ~ ~ ~ minecraft:iron_block run function _your_namespace:custom_blocks/_groups/minecraft_iron_block
execute if score #total_vanilla_polished_deepslate _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_polished_deepslate] unless block ~ ~ ~ minecraft:polished_deepslate run function _your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
execute if score #total_vanilla_raw_iron_block _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vanilla.minecraft_raw_iron_block] unless block ~ ~ ~ minecraft:raw_iron_block run function _your_namespace:custom_blocks/_groups/minecraft_raw_iron_block

