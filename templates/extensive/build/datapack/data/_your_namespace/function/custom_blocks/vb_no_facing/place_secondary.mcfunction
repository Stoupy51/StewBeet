
#> _your_namespace:custom_blocks/vb_no_facing/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/vb_no_facing/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.vb_no_facing
tag @s add _your_namespace.vanilla.minecraft_cobblestone

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.vb_no_facing"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:vb_no_facing"]
data modify entity @s transformation.scale set value [1.002f, 1.002f, 1.002f]
data modify entity @s brightness set value {block: 15, sky: 15}

