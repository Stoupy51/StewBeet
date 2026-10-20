
#> _your_namespace:custom_blocks/crate/destroy
#
# @executed	as @e[type=item_display,tag=_your_namespace.custom_block,distance=..0.1]
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_diamond_block
#

# Replace the item with the custom one
execute as @n[type=item, nbt={Item: {id: "minecraft:diamond_block"}}, distance=..1] run function _your_namespace:custom_blocks/crate/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_diamond_block _your_namespace.data 1
scoreboard players remove #total_crate _your_namespace.data 1

# Kill the custom block entity
kill @s

