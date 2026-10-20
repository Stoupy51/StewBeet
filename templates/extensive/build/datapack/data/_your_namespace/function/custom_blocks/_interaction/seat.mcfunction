
#> _your_namespace:custom_blocks/_interaction/seat
#
# @executed	positioned ~ ~0.5 ~
#
# @within	_your_namespace:custom_blocks/chair/sit [ positioned ~ ~0.5 ~ ]
#

tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add _your_namespace.seat
ride @p[tag=_your_namespace.user] mount @s
scoreboard players add #seats _your_namespace.data 1

