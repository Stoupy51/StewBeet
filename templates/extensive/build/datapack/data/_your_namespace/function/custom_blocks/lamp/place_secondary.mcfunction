
#> _your_namespace:custom_blocks/lamp/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/lamp/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.lamp
tag @s add _your_namespace.vanilla.minecraft_light

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.lamp",fallback: "Lamp"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:lamp"]
function _your_namespace:custom_blocks/compute_brightness

# Interaction breaking the block when hit
summon interaction ~ ~-0.5 ~ {width: 1.01f, height: 1.01f, response: true, Tags: ["global.ignore", "global.ignore.kill", "smithed.entity", "_your_namespace.interaction", "_your_namespace.lamp"]}

