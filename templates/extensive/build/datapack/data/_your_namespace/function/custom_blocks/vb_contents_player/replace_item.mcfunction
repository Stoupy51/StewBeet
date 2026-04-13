
#> _your_namespace:custom_blocks/vb_contents_player/replace_item
#
# @executed	as @n[type=item,nbt={...},distance=..1]
#
# @within	_your_namespace:custom_blocks/vb_contents_player/destroy [ as @n[type=item,nbt={...},distance=..1] ]
#

# Replace the item with the custom one
data modify entity @s Item.components set from storage _your_namespace:items all.vb_contents_player.components
data modify entity @s Item.id set from storage _your_namespace:items all.vb_contents_player.id

