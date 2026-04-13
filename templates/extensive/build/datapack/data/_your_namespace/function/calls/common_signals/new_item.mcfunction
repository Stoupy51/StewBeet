
#> _your_namespace:calls/common_signals/new_item
#
# @within	#common_signals:signals/on_new_item
#

# If the item is from a custom ore, launch the on_ore_destroyed function
execute if data entity @s Item.components."minecraft:custom_data".common_signals.temp at @s align xyz run function _your_namespace:calls/common_signals/on_ore_destroyed

# If the item is from a custom block alternative, launch the item_frame destroy function
execute if data entity @s Item.components."minecraft:custom_data"._your_namespace.item_frame_destroy at @s align xyz run function _your_namespace:calls/common_signals/on_item_frame_destroy

