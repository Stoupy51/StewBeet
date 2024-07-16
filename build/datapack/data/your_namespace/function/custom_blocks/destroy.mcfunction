
#> your_namespace:custom_blocks/destroy
#
# @within	your_namespace:v1.0.0/tick_2
#			your_namespace:v1.0.0/second
#			your_namespace:v1.0.0/second_5
#

execute if entity @s[tag=your_namespace.vanilla.minecraft_deepslate_iron_ore] unless block ~ ~ ~ minecraft:deepslate_iron_ore run function your_namespace:custom_blocks/_groups/minecraft_deepslate_iron_ore
execute if entity @s[tag=your_namespace.vanilla.minecraft_iron_block] unless block ~ ~ ~ minecraft:iron_block run function your_namespace:custom_blocks/_groups/minecraft_iron_block
execute if entity @s[tag=your_namespace.vanilla.minecraft_iron_ore] unless block ~ ~ ~ minecraft:iron_ore run function your_namespace:custom_blocks/_groups/minecraft_iron_ore
execute if entity @s[tag=your_namespace.vanilla.minecraft_raw_iron_block] unless block ~ ~ ~ minecraft:raw_iron_block run function your_namespace:custom_blocks/_groups/minecraft_raw_iron_block
execute if entity @s[tag=your_namespace.vanilla.minecraft_stone] unless block ~ ~ ~ minecraft:stone run function your_namespace:custom_blocks/_groups/minecraft_stone

