
#> _your_namespace:custom_blocks/steel_block/place_main
#
# @within	_your_namespace:custom_blocks/place
#

tag @s add _your_namespace.placer
setblock ~ ~ ~ air
setblock ~ ~ ~ minecraft:iron_block
execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function _your_namespace:custom_blocks/steel_block/place_secondary
tag @s remove _your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_iron_block _your_namespace.data 1
scoreboard players add #total_steel_block _your_namespace.data 1

