
#> _your_namespace:custom_blocks/_aim/main
#
# @executed	align xyz & positioned ~0.5 ~0.5 ~0.5
#
# @within	_your_namespace:custom_blocks/plank_slab/place_main [ align xyz & positioned ~0.5 ~0.5 ~0.5 ]
#			_your_namespace:custom_blocks/plank_stairs/place_main [ align xyz & positioned ~0.5 ~0.5 ~0.5 ]
#

tag @s add _your_namespace.aimed
scoreboard players set #upper _your_namespace.data 0
scoreboard players set #floor _your_namespace.data 0
scoreboard players set #inside _your_namespace.data 0
scoreboard players set #steps _your_namespace.data 0
execute as @p[tag=_your_namespace.placer] at @s anchored eyes positioned ^ ^ ^ anchored feet run function _your_namespace:custom_blocks/_aim/ray
kill @s

