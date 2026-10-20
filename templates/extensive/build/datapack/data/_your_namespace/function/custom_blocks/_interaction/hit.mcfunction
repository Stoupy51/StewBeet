
#> _your_namespace:custom_blocks/_interaction/hit
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:custom_blocks/interaction_hit
#

advancement revoke @s only _your_namespace:custom_blocks/interaction_hit
tag @s add _your_namespace.breaker
execute as @e[type=interaction, tag=_your_namespace.interaction, distance=..8] if data entity @s attack run function _your_namespace:custom_blocks/_interaction/dispatch_hit
tag @s remove _your_namespace.breaker

