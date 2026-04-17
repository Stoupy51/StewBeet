
#> _your_namespace:custom_blocks/vb_block_states/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/vb_block_states/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.vb_block_states
tag @s add _your_namespace.vanilla.minecraft_furnace

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.vb_block_states"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:vb_block_states"]
data modify entity @s transformation.scale set value [1.002f, 1.002f, 1.002f]
data modify entity @s brightness set value {block: 15, sky: 15}

# Apply rotation
execute if score #rotation _your_namespace.data matches 1 run data modify entity @s Rotation[0] set value 180.0f
execute if score #rotation _your_namespace.data matches 2 run data modify entity @s Rotation[0] set value 270.0f
execute if score #rotation _your_namespace.data matches 3 run data modify entity @s Rotation[0] set value 0.0f
execute if score #rotation _your_namespace.data matches 4 run data modify entity @s Rotation[0] set value 90.0f

