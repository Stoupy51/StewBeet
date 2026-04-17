
#> _your_namespace:calls/common_signals/item_frame_destroy_alt
#
# @executed	at @s
#
# @within	_your_namespace:calls/common_signals/on_item_frame_destroy [ at @s ]
#			_your_namespace:calls/common_signals/on_item_frame_destroy [ at @s & as @n[type=item,nbt={Item:{id:"minecraft:item_frame"}},distance=..1] ]
#

# Give a new tag to the item frame
data modify storage _your_namespace:temp Tags set value []
data modify storage _your_namespace:temp Tags append from entity @s Item.components."minecraft:custom_data"._your_namespace.alt_destroy
data modify entity @n[type=item, nbt={Item: {id: "minecraft:item_frame"}}, distance=..1] Tags set from storage _your_namespace:temp Tags

# Remove the custom block "properly"
execute as @n[type=item, nbt={Item: {id: "minecraft:item_frame"}}, distance=..1] run function _your_namespace:custom_blocks/_groups/minecraft_item_frame

