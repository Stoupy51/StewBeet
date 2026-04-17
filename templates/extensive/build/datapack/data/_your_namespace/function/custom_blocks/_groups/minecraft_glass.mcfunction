
#> _your_namespace:custom_blocks/_groups/minecraft_glass
#
# @executed	as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s
#
# @within	_your_namespace:custom_blocks/destroy
#

execute if score #total_vb_visual_facing _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vb_visual_facing] run function _your_namespace:custom_blocks/vb_visual_facing/destroy

