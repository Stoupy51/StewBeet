
#> _your_namespace:custom_blocks/plank_stairs/place_main
#
# @within	_your_namespace:custom_blocks/place
#

tag @s add _your_namespace.placer
execute align xyz positioned ~0.5 ~0.5 ~0.5 summon marker run function _your_namespace:custom_blocks/_aim/main
function _your_namespace:custom_blocks/get_rotation
setblock ~ ~ ~ air strict
execute if score #rotation _your_namespace.data matches 1 if score #upper _your_namespace.data matches 0 run setblock ~ ~ ~ minecraft:oak_stairs[half=bottom, facing=south]
execute if score #rotation _your_namespace.data matches 1 if score #upper _your_namespace.data matches 1 run setblock ~ ~ ~ minecraft:oak_stairs[half=top, facing=south]
execute if score #rotation _your_namespace.data matches 2 if score #upper _your_namespace.data matches 0 run setblock ~ ~ ~ minecraft:oak_stairs[half=bottom, facing=west]
execute if score #rotation _your_namespace.data matches 2 if score #upper _your_namespace.data matches 1 run setblock ~ ~ ~ minecraft:oak_stairs[half=top, facing=west]
execute if score #rotation _your_namespace.data matches 3 if score #upper _your_namespace.data matches 0 run setblock ~ ~ ~ minecraft:oak_stairs[half=bottom, facing=north]
execute if score #rotation _your_namespace.data matches 3 if score #upper _your_namespace.data matches 1 run setblock ~ ~ ~ minecraft:oak_stairs[half=top, facing=north]
execute if score #rotation _your_namespace.data matches 4 if score #upper _your_namespace.data matches 0 run setblock ~ ~ ~ minecraft:oak_stairs[half=bottom, facing=east]
execute if score #rotation _your_namespace.data matches 4 if score #upper _your_namespace.data matches 1 run setblock ~ ~ ~ minecraft:oak_stairs[half=top, facing=east]
execute align xyz positioned ~0.5 ~0.5 ~0.5 summon item_display at @s run function _your_namespace:custom_blocks/plank_stairs/place_secondary
tag @s remove _your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_oak_stairs _your_namespace.data 1
scoreboard players add #total_plank_stairs _your_namespace.data 1

