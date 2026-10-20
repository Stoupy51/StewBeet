
#> _your_namespace:custom_blocks/_aim/ray
#
# @executed	as @p[tag=_your_namespace.placer] & at @s & anchored eyes & positioned ^ ^ ^ & anchored feet
#
# @within	_your_namespace:custom_blocks/_aim/main [ as @p[tag=_your_namespace.placer] & at @s & anchored eyes & positioned ^ ^ ^ & anchored feet ]
#			_your_namespace:custom_blocks/_aim/ray [ positioned ^ ^ ^0.05 ]
#

# A box test from 0.5 below a point holds when the point is in the block, from 1 below when it is in its upper half
scoreboard players add #steps _your_namespace.data 1
execute if score #steps _your_namespace.data matches 120.. run return 0
scoreboard players operation #was_inside _your_namespace.data = #inside _your_namespace.data
execute positioned ~-0.5 ~-0.5 ~-0.5 store success score #inside _your_namespace.data if entity @e[type=marker, tag=_your_namespace.aimed, dx=0, dy=0, dz=0]
execute if score #inside _your_namespace.data matches 1 positioned ~-0.5 ~-1 ~-0.5 store success score #upper _your_namespace.data if entity @e[type=marker, tag=_your_namespace.aimed, dx=0, dy=0, dz=0]
execute if score #was_inside _your_namespace.data matches 1 if score #inside _your_namespace.data matches 0 positioned ~-0.5 ~0.5 ~-0.5 store success score #floor _your_namespace.data if entity @e[type=marker, tag=_your_namespace.aimed, dx=0, dy=0, dz=0]
execute if score #was_inside _your_namespace.data matches 1 if score #inside _your_namespace.data matches 0 run return 0
execute positioned ^ ^ ^0.05 run function _your_namespace:custom_blocks/_aim/ray

