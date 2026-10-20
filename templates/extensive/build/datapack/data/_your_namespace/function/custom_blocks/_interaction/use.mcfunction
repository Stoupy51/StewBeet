
#> _your_namespace:custom_blocks/_interaction/use
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/_interaction/used [ at @s ]
#

data remove entity @s interaction
execute if entity @s[tag=_your_namespace.chair] run return run function _your_namespace:custom_blocks/chair/sit

