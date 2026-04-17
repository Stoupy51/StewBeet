
#> _your_namespace:custom_blocks/vb_contents_player/destroy
#
# @executed	as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_item_frame
#

# Replace the item with the custom one
execute as @n[type=item, nbt={Item: {components: {"minecraft:custom_data": {_your_namespace: {item_frame_destroy: true}}}}}, distance=..1] run function _your_namespace:custom_blocks/vb_contents_player/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_item_frame _your_namespace.data 1
scoreboard players remove #total_vb_contents_player _your_namespace.data 1

# Kill the custom block entity
kill @s

