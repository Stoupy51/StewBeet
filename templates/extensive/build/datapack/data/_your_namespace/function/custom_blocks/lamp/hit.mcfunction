
#> _your_namespace:custom_blocks/lamp/hit
#
# @executed	at @s & positioned ~ ~0.5 ~
#
# @within	_your_namespace:custom_blocks/_interaction/dispatch_hit [ at @s & positioned ~ ~0.5 ~ ]
#

# Break it, dropping nothing for a creative player
execute store success score #no_drop _your_namespace.data if entity @p[tag=_your_namespace.breaker, gamemode=creative]
function _your_namespace:custom_blocks/_interaction/break

