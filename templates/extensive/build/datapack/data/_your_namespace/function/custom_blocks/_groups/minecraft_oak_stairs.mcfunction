
#> _your_namespace:custom_blocks/_groups/minecraft_oak_stairs
#
# @executed	as @e[type=item_display,tag=_your_namespace.custom_block,distance=..0.1]
#
# @within	_your_namespace:custom_blocks/destroy
#

execute if score #total_plank_stairs _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.plank_stairs] run function _your_namespace:custom_blocks/plank_stairs/destroy

