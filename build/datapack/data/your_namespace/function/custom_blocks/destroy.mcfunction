
#> your_namespace:custom_blocks/destroy
#
# @within	your_namespace:v1.0.0/tick_2
#			your_namespace:v1.0.0/second
#			your_namespace:v1.0.0/second_5
#			your_namespace:calls/common_signals/on_ore_destroyed
#

execute if score #total_vanilla_iron_block your_namespace.data matches 1.. if entity @s[tag=your_namespace.vanilla.minecraft_iron_block] unless block ~ ~ ~ minecraft:iron_block run function your_namespace:custom_blocks/_groups/minecraft_iron_block
execute if score #total_vanilla_polished_deepslate your_namespace.data matches 1.. if entity @s[tag=your_namespace.vanilla.minecraft_polished_deepslate] unless block ~ ~ ~ minecraft:polished_deepslate run function your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
execute if score #total_vanilla_raw_iron_block your_namespace.data matches 1.. if entity @s[tag=your_namespace.vanilla.minecraft_raw_iron_block] unless block ~ ~ ~ minecraft:raw_iron_block run function your_namespace:custom_blocks/_groups/minecraft_raw_iron_block
execute if score #total_vanilla_stone your_namespace.data matches 1.. if entity @s[tag=your_namespace.vanilla.minecraft_stone] unless block ~ ~ ~ minecraft:stone run function your_namespace:custom_blocks/_groups/minecraft_stone

