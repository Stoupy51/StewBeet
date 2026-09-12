
#> _your_namespace:custom_blocks/vb_visual_facing/place_main
#
# @within	_your_namespace:custom_blocks/place
#

tag @s add _your_namespace.placer
function _your_namespace:custom_blocks/get_rotation
setblock ~ ~ ~ air strict
setblock ~ ~ ~ minecraft:glass
execute align xyz positioned ~0.5 ~0.5 ~0.5 summon item_display at @s run function _your_namespace:custom_blocks/vb_visual_facing/place_secondary
tag @s remove _your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_glass _your_namespace.data 1
scoreboard players add #total_vb_visual_facing _your_namespace.data 1

