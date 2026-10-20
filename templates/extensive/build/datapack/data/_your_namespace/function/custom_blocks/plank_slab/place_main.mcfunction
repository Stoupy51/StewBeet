
#> _your_namespace:custom_blocks/plank_slab/place_main
#
# @within	_your_namespace:custom_blocks/place
#

tag @s add _your_namespace.placer
execute align xyz positioned ~0.5 ~0.5 ~0.5 summon marker run function _your_namespace:custom_blocks/_aim/main
setblock ~ ~ ~ air strict
execute if score #upper _your_namespace.data matches 0 run setblock ~ ~ ~ minecraft:oak_slab[type=bottom]
execute if score #upper _your_namespace.data matches 1 run setblock ~ ~ ~ minecraft:oak_slab[type=top]
execute align xyz positioned ~0.5 ~0.5 ~0.5 summon item_display at @s run function _your_namespace:custom_blocks/plank_slab/place_secondary
tag @s remove _your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_oak_slab _your_namespace.data 1
scoreboard players add #total_plank_slab _your_namespace.data 1

