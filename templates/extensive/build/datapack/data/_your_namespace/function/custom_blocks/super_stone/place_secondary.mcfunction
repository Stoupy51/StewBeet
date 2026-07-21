
#> _your_namespace:custom_blocks/super_stone/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/super_stone/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.super_stone
tag @s add _your_namespace.vanilla.minecraft_cobblestone

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.super_stone"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:super_stone"]
data modify entity @s transformation.scale set value [1.002f, 1.002f, 1.002f]
function _your_namespace:custom_blocks/compute_brightness

say Omg, @p[tag=_your_namespace.placer] placed the super stone block!
particle minecraft:explosion ~ ~ ~

