
#> _your_namespace:advancements/open_manual
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:open_manual
#

# Revoke advancement and reset score
advancement revoke @s only _your_namespace:open_manual
scoreboard players set @s _your_namespace.open_manual 0

# Show manual dialog if holding the manual
execute if items entity @s weapon.* *[custom_data~{_your_namespace:{manual:true}}] run dialog show @s _your_namespace:manual/page_1

