
#> _your_namespace:custom_blocks/super_stone/replace_item
#
# @executed	as @n[type=item,nbt={Item: {id: "minecraft:cobblestone"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/super_stone/destroy [ as @n[type=item,nbt={Item: {id: "minecraft:cobblestone"}},distance=..1] ]
#

data modify entity @s Item.components set from storage _your_namespace:items all.super_stone.components
data modify entity @s Item.id set from storage _your_namespace:items all.super_stone.id

