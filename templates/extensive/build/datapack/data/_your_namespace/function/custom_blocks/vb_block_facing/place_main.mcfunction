
#> _your_namespace:custom_blocks/vb_block_facing/place_main
#
# @within	_your_namespace:custom_blocks/place
#

tag @s add _your_namespace.placer
function _your_namespace:custom_blocks/get_rotation
setblock ~ ~ ~ air strict
execute if score #rotation _your_namespace.data matches 1 run setblock ~ ~ ~ minecraft:furnace[facing=north]{CustomName: {translate: "_your_namespace.vb_block_facing"}}
execute if score #rotation _your_namespace.data matches 2 run setblock ~ ~ ~ minecraft:furnace[facing=east]{CustomName: {translate: "_your_namespace.vb_block_facing"}}
execute if score #rotation _your_namespace.data matches 3 run setblock ~ ~ ~ minecraft:furnace[facing=south]{CustomName: {translate: "_your_namespace.vb_block_facing"}}
execute if score #rotation _your_namespace.data matches 4 run setblock ~ ~ ~ minecraft:furnace[facing=west]{CustomName: {translate: "_your_namespace.vb_block_facing"}}
execute align xyz positioned ~0.5 ~0.5 ~0.5 summon item_display at @s run function _your_namespace:custom_blocks/vb_block_facing/place_secondary
tag @s remove _your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_furnace _your_namespace.data 1
scoreboard players add #total_vb_block_facing _your_namespace.data 1

