
#> _your_namespace:custom_blocks/vb_visual_facing/destroy
#
# @executed	as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_glass
#

# Replace the item with the custom one
execute as @n[type=item, nbt={Item: {id: "minecraft:glass"}}, distance=..1] run function _your_namespace:custom_blocks/vb_visual_facing/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_glass _your_namespace.data 1
scoreboard players remove #total_vb_visual_facing _your_namespace.data 1

# Kill the custom block entity
kill @s

