
#> _your_namespace:v3.0.0/unload/safe_kill
#
# @executed	as @e[tag=_your_namespace.chair] & at @s
#
# @within	_your_namespace:v3.0.0/unload [ as @e[tag=_your_namespace.chair] & at @s ]
#			_your_namespace:v3.0.0/unload [ at @s ]
#			_your_namespace:v3.0.0/unload [ as @e[tag=_your_namespace.lamp] & at @s ]
#			_your_namespace:v3.0.0/unload [ as @e[tag=_your_namespace.new] & at @s ]
#			_your_namespace:v3.0.0/unload [ as @e[tag=_your_namespace.unloaded] & at @s ]
#

# This function is used to safely kill entities by teleporting them to the void before killing them to prevent item drops
tp @s ~ -10000 ~
kill @s

