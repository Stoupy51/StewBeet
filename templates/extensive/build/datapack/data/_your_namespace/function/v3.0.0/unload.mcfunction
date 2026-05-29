
#> _your_namespace:v3.0.0/unload
#
# @within	#_your_namespace:unload
#			_your_namespace:v3.0.0/unload_with_libraries
#

# Clear custom items
clear @a *[custom_data~{"_your_namespace":{}}]

# Destroy custom blocks
execute as @e[type=minecraft:item_display,tag=_your_namespace.custom_block] at @s run function _your_namespace:v3.0.0/unload/destroy_block

# Kill entities with custom tags
execute as @e[tag=_your_namespace.new] at @s run function _your_namespace:v3.0.0/unload/safe_kill

# Remove scoreboard objectives
scoreboard objectives remove _your_namespace.data
scoreboard objectives remove _your_namespace.open_manual
scoreboard objectives remove load.status

# Clear storages
data remove storage _your_namespace:items all
data remove storage _your_namespace:temp Tags

