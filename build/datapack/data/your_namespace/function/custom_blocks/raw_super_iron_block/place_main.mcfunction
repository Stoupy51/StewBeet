
#> your_namespace:custom_blocks/raw_super_iron_block/place_main
#
# @within	your_namespace:custom_blocks/place
#

tag @s add your_namespace.placer
setblock ~ ~ ~ air
setblock ~ ~ ~ minecraft:raw_iron_block
execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function your_namespace:custom_blocks/raw_super_iron_block/place_secondary
tag @s remove your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks your_namespace.data 1
scoreboard players add #total_vanilla_raw_iron_block your_namespace.data 1
scoreboard players add #total_raw_super_iron_block your_namespace.data 1

