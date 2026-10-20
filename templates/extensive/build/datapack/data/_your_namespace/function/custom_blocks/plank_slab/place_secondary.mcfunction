
#> _your_namespace:custom_blocks/plank_slab/place_secondary
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/plank_slab/place_main [ at @s ]
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add _your_namespace.custom_block
tag @s add _your_namespace.plank_slab
tag @s add _your_namespace.vanilla.minecraft_oak_slab

# Add a custom name
data merge entity @s {CustomName: {translate: "_your_namespace.plank_slab"}}

# Modify item display entity to match the custom block
item replace entity @s contents with minecraft:furnace[item_model="_your_namespace:plank_slab"]
function _your_namespace:custom_blocks/compute_brightness

# Show the model flipped on the upper half
execute if score #upper _your_namespace.data matches 1 run data modify entity @s item.components."minecraft:item_model" set value "_your_namespace:plank_slab_up"

