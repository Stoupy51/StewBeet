
#> _your_namespace:custom_blocks/vb_no_facing/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:cobblestone"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/vb_no_facing/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:cobblestone"}},distance=..1] ]
#

# Replace the item with the custom one
data modify entity @s Item.components set from storage _your_namespace:items all.vb_no_facing.components
data modify entity @s Item.id set from storage _your_namespace:items all.vb_no_facing.id

