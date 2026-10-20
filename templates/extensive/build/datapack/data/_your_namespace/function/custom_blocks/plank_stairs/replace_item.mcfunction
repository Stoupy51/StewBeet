
#> _your_namespace:custom_blocks/plank_stairs/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:oak_stairs"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/plank_stairs/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:oak_stairs"}},distance=..1] ]
#

# Replace the item with the custom one
data modify entity @s Item.components set from storage _your_namespace:items all.plank_stairs.components
data modify entity @s Item.id set from storage _your_namespace:items all.plank_stairs.id

