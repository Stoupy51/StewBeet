
#> your_namespace:custom_blocks/_groups/minecraft_iron_block
#
# @within	your_namespace:custom_blocks/destroy
#

execute if score #total_super_iron_block your_namespace.data matches 1.. if entity @s[tag=your_namespace.super_iron_block] run function your_namespace:custom_blocks/super_iron_block/destroy

