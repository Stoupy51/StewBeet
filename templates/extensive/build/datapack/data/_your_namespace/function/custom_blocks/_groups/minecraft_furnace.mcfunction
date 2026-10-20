
#> _your_namespace:custom_blocks/_groups/minecraft_furnace
#
# @executed	as @e[type=item_display,tag=_your_namespace.custom_block,distance=..0.1]
#
# @within	_your_namespace:custom_blocks/destroy
#

execute if score #total_vb_block_facing _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vb_block_facing] run function _your_namespace:custom_blocks/vb_block_facing/destroy
execute if score #total_vb_block_states _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.vb_block_states] run function _your_namespace:custom_blocks/vb_block_states/destroy
execute if score #total_fast_furnace _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.fast_furnace] run function _your_namespace:custom_blocks/fast_furnace/destroy

