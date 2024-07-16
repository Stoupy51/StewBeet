
#> your_namespace:custom_blocks/super_iron_ore/replace_item
#
# @within	your_namespace:custom_blocks/super_iron_ore/destroy
#

data modify entity @s Item.components set from storage your_namespace:items all.super_iron_ore.components
data modify entity @s Item.id set from storage your_namespace:items all.super_iron_ore.id

