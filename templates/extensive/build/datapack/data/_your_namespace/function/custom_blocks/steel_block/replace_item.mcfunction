
#> _your_namespace:custom_blocks/steel_block/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:iron_block"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/steel_block/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:iron_block"}},distance=..1] ]
#

data modify entity @s Item.components set from storage _your_namespace:items all.steel_block.components
data modify entity @s Item.id set from storage _your_namespace:items all.steel_block.id

