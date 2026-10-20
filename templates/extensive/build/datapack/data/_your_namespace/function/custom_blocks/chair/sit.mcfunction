
#> _your_namespace:custom_blocks/chair/sit
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/_interaction/use
#

execute as @p[tag=_your_namespace.user] if predicate {type: "minecraft:entity_properties", entity: "this", predicate: {vehicle: {}}} run return fail
execute positioned ~ ~0.5 ~ summon item_display run function _your_namespace:custom_blocks/_interaction/seat

