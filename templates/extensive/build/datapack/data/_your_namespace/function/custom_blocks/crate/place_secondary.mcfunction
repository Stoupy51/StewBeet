
#> _your_namespace:custom_blocks/crate/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/crate/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.crate
tag @s add _your_namespace.vanilla.minecraft_diamond_block

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.crate"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:crate"]
function _your_namespace:custom_blocks/compute_brightness

