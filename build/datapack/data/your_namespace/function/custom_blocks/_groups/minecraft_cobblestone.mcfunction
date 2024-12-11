
#> your_namespace:custom_blocks/_groups/minecraft_cobblestone
#
# @within	your_namespace:custom_blocks/destroy
#

execute if score #total_super_stone your_namespace.data matches 1.. if entity @s[tag=your_namespace.super_stone] run function your_namespace:custom_blocks/super_stone/destroy

