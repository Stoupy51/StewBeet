
#> _your_namespace:custom_blocks/_groups/minecraft_item_frame
#
# @executed	as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s
#
# @within	_your_namespace:custom_blocks/destroy
#			_your_namespace:calls/common_signals/item_frame_destroy_alt [ as @n[type=item,nbt={Item:{id:"minecraft:item_frame"}},distance=..1] ]
#

execute if score #total_vb_contents _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vb_contents] run function _your_namespace:custom_blocks/vb_contents/destroy
execute if score #total_vb_contents_player _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vb_contents_player] run function _your_namespace:custom_blocks/vb_contents_player/destroy
execute if score #total_vb_contents_frame _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vb_contents_frame] run function _your_namespace:custom_blocks/vb_contents_frame/destroy

