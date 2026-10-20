
#> _your_namespace:ranged_weapon/crossbow/loaded
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:ranged_weapon/crossbow_loaded
#

advancement revoke @s only _your_namespace:ranged_weapon/crossbow_loaded
execute if items entity @s weapon.mainhand *[custom_data~{_your_namespace: {crossbow: true}}] if data entity @s SelectedItem.components."minecraft:charged_projectiles"[0] unless data entity @s SelectedItem.components."minecraft:charged_projectiles"[0].components."minecraft:custom_data"._your_namespace.bolt run function _your_namespace:ranged_weapon/crossbow/unload_mainhand
execute if items entity @s weapon.offhand *[custom_data~{_your_namespace: {crossbow: true}}] if data entity @s equipment.offhand.components."minecraft:charged_projectiles"[0] unless data entity @s equipment.offhand.components."minecraft:charged_projectiles"[0].components."minecraft:custom_data"._your_namespace.bolt run function _your_namespace:ranged_weapon/crossbow/unload_offhand

