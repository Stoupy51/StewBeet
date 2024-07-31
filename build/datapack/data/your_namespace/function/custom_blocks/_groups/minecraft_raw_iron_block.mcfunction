
#> your_namespace:custom_blocks/_groups/minecraft_raw_iron_block
#
# @within	your_namespace:custom_blocks/destroy
#

execute if score #total_raw_super_iron_block your_namespace.data matches 1.. if entity @s[tag=your_namespace.raw_super_iron_block] run function your_namespace:custom_blocks/raw_super_iron_block/destroy

