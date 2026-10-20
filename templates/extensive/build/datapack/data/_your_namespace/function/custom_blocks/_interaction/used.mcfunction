
#> _your_namespace:custom_blocks/_interaction/used
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:custom_blocks/interaction_used
#

advancement revoke @s only _your_namespace:custom_blocks/interaction_used
tag @s add _your_namespace.user
execute as @e[type=interaction, tag=_your_namespace.interaction, distance=..8] if data entity @s interaction at @s run function _your_namespace:custom_blocks/_interaction/use
tag @s remove _your_namespace.user

