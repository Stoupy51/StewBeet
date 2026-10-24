
#> _your_namespace:custom_blocks/plank_stairs/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/plank_stairs/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.plank_stairs
tag @s add _your_namespace.vanilla.minecraft_oak_stairs

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.plank_stairs",fallback: "Plank Stairs"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:plank_stairs"]
function _your_namespace:custom_blocks/compute_brightness

# Show the copy of the model turned towards the placer
data modify entity @s transformation.left_rotation set value [0.0f, 1.0f, 0.0f, 0.0f]
execute if score #rotation _your_namespace.data matches 2 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_y90"
execute if score #rotation _your_namespace.data matches 3 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_y180"
execute if score #rotation _your_namespace.data matches 4 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_y270"

# Show the model flipped on the upper half
execute if score #upper _your_namespace.data matches 1 if score #rotation _your_namespace.data matches 2 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_y90_up"
execute if score #upper _your_namespace.data matches 1 if score #rotation _your_namespace.data matches 3 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_y180_up"
execute if score #upper _your_namespace.data matches 1 if score #rotation _your_namespace.data matches 4 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_y270_up"
execute if score #upper _your_namespace.data matches 1 if score #rotation _your_namespace.data matches 1 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_stairs_up"

# Show the model of the state the host is in
function _your_namespace:custom_blocks/plank_stairs/follow_host

# Add tag for loop every second
tag @s add _your_namespace.second
scoreboard players add #second_entities _your_namespace.data 1

