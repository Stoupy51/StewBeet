
#> _your_namespace:custom_blocks/_interaction/dispatch_hit
#
# @executed	as @e[type=interaction,tag=_your_namespace.interaction,distance=..8]
#
# @within	_your_namespace:custom_blocks/_interaction/hit [ as @e[type=interaction,tag=_your_namespace.interaction,distance=..8] ]
#

data remove entity @s attack
execute if entity @s[tag=_your_namespace.chair] at @s positioned ~ ~0.5 ~ run return run function _your_namespace:custom_blocks/chair/hit
execute if entity @s[tag=_your_namespace.lamp] at @s positioned ~ ~0.5 ~ run return run function _your_namespace:custom_blocks/lamp/hit

