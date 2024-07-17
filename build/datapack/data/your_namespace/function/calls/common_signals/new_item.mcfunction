
#> your_namespace:calls/common_signals/new_item
#
# @within	#common_signals:signals/on_new_item
#

# If the item is from a custom ore, launch the on_ore_destroyed function
execute if data entity @s Item.components."minecraft:custom_data".common_signals.temp at @s align xyz run function your_namespace:calls/common_signals/on_ore_destroyed

