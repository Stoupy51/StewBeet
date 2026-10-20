
#> _your_namespace:ranged_weapon/crossbow/unload_mainhand
#
# @executed	as the player & at current position
#
# @within	_your_namespace:ranged_weapon/crossbow/loaded
#

# Give back what it loaded, unless the player is in creative where loading costs nothing
execute if entity @s[gamemode=!creative] run summon item ~ ~1 ~ {Item: {id: "minecraft:stone"}, Tags: ["_your_namespace.unloaded"], PickupDelay: 0s}
execute if entity @s[gamemode=!creative] run data modify entity @n[type=item, tag=_your_namespace.unloaded] Item set from entity @s SelectedItem.components."minecraft:charged_projectiles"[0]
tag @n[type=item, tag=_your_namespace.unloaded] remove _your_namespace.unloaded
item modify entity @s weapon.mainhand {type: "minecraft:set_components", components: {"minecraft:charged_projectiles": []}}

