
#> _your_namespace:custom_blocks/vb_contents_player/place_secondary
#
# @executed	as @n[tag=_your_namespace.new] & at @s
#
# @within	_your_namespace:custom_blocks/vb_contents_player/place_main [ as @n[tag=_your_namespace.new] & at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s remove _your_namespace.new
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.vb_contents_player
tag @s add _your_namespace.vanilla.minecraft_item_frame

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.vb_contents_player"}}

# Modify item frame entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:vb_contents_player", custom_data={_your_namespace: {item_frame_destroy: true, alt_destroy: "_your_namespace.vb_contents_player"}}]
execute store result entity @s Facing byte 1 run scoreboard players get #item_frame_facing _your_namespace.data

# Update position (fixes a Minecraft bug)
execute at @s run tp @s ^ ^ ^0.1

# Force ground position
data modify entity @s Facing set value 1b

# Apply rotation based on player direction
execute if score #rotation _your_namespace.data matches 1 run data modify entity @s ItemRotation set value 4b
execute if score #rotation _your_namespace.data matches 2 run data modify entity @s ItemRotation set value 6b
execute if score #rotation _your_namespace.data matches 3 run data modify entity @s ItemRotation set value 0b
execute if score #rotation _your_namespace.data matches 4 run data modify entity @s ItemRotation set value 2b

