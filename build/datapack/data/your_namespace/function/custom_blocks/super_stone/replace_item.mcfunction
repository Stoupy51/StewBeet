
#> your_namespace:custom_blocks/super_stone/replace_item
#
# @within	your_namespace:custom_blocks/super_stone/destroy
#

data modify entity @s Item.components set from storage your_namespace:items all.super_stone.components
data modify entity @s Item.id set from storage your_namespace:items all.super_stone.id

