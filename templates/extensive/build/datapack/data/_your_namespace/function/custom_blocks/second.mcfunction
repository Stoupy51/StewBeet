
#> _your_namespace:custom_blocks/second
#
# @executed	as @e[tag=_your_namespace.second] & at @s
#
# @within	_your_namespace:v3.0.0/second [ as @e[tag=_your_namespace.second] & at @s ]
#

execute if entity @s[tag=_your_namespace.plank_stairs] run function _your_namespace:custom_blocks/plank_stairs/second
execute if entity @s[tag=_your_namespace.fast_furnace] run function _your_namespace:custom_blocks/fast_furnace/second
execute if entity @s[tag=_your_namespace.steel_block] run function _your_namespace:custom_blocks/steel_block/second

