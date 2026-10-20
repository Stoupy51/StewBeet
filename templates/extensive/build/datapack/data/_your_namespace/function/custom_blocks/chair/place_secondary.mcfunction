
#> _your_namespace:custom_blocks/chair/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/chair/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.chair
tag @s add _your_namespace.vanilla.minecraft_barrier

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.chair"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:chair"]
function _your_namespace:custom_blocks/compute_brightness

# Apply rotation
execute if score #rotation _your_namespace.data matches 1 run data modify entity @s Rotation[0] set value 180.0f
execute if score #rotation _your_namespace.data matches 2 run data modify entity @s Rotation[0] set value 270.0f
execute if score #rotation _your_namespace.data matches 3 run data modify entity @s Rotation[0] set value 0.0f
execute if score #rotation _your_namespace.data matches 4 run data modify entity @s Rotation[0] set value 90.0f

# Interaction breaking the block when hit
summon interaction ~ ~-0.5 ~ {width: 1.01f, height: 1.01f, response: true, Tags: ["global.ignore", "global.ignore.kill", "smithed.entity", "_your_namespace.interaction", "_your_namespace.chair"]}

