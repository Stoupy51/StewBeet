
#> _your_namespace:custom_blocks/_interaction/break
#
# @executed	at @s & positioned ~ ~0.5 ~
#
# @within	_your_namespace:custom_blocks/chair/hit
#			_your_namespace:custom_blocks/lamp/hit
#

setblock ~ ~ ~ air
execute as @e[type=item_display, tag=_your_namespace.custom_block, distance=..0.1] run function _your_namespace:custom_blocks/destroy
scoreboard players set #no_drop _your_namespace.data 0

