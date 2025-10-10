
#> _your_namespace:custom_blocks/raw_steel_block/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:raw_iron_block"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/raw_steel_block/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:raw_iron_block"}},distance=..1] ]
#

# Replace the item with the custom one
data modify entity @s Item.components set from storage _your_namespace:items all.raw_steel_block.components
data modify entity @s Item.id set from storage _your_namespace:items all.raw_steel_block.id

