
#> _your_namespace:custom_blocks/fast_furnace/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/fast_furnace/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.fast_furnace
tag @s add _your_namespace.vanilla.minecraft_furnace

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.fast_furnace"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:fast_furnace"]
function _your_namespace:custom_blocks/compute_brightness

# Apply rotation
execute if score #rotation _your_namespace.data matches 1 run data modify entity @s Rotation[0] set value 180.0f
execute if score #rotation _your_namespace.data matches 2 run data modify entity @s Rotation[0] set value 270.0f
execute if score #rotation _your_namespace.data matches 3 run data modify entity @s Rotation[0] set value 0.0f
execute if score #rotation _your_namespace.data matches 4 run data modify entity @s Rotation[0] set value 90.0f

# Show the model of the state the host is in
function _your_namespace:custom_blocks/fast_furnace/follow_host

# Add tag for loop every tick
tag @s add _your_namespace.tick
scoreboard players add #tick_entities _your_namespace.data 1

# Add tag for loop every second
tag @s add _your_namespace.second
scoreboard players add #second_entities _your_namespace.data 1

