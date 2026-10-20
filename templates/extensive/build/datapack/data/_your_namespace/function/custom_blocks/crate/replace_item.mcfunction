
#> _your_namespace:custom_blocks/crate/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:diamond_block"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/crate/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:diamond_block"}},distance=..1] ]
#

# Replace the item with the custom one
data modify entity @s Item.components set from storage _your_namespace:items all.crate.components
data modify entity @s Item.id set from storage _your_namespace:items all.crate.id

