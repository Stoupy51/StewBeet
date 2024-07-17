
#> your_namespace:custom_blocks/super_iron_ore/replace_item
#
# @within	your_namespace:custom_blocks/super_iron_ore/destroy
#

# If silk touch applied
execute if score #is_silk_touch your_namespace.data matches 1 run data modify entity @s Item.id set from storage your_namespace:items all.super_iron_ore.id
execute if score #is_silk_touch your_namespace.data matches 1 run data modify entity @s Item.components set from storage your_namespace:items all.super_iron_ore.components

# Else, no silk touch
execute if score #is_silk_touch your_namespace.data matches 0 run data modify entity @s Item.id set from storage your_namespace:items all.raw_super_iron.id
execute if score #is_silk_touch your_namespace.data matches 0 run data modify entity @s Item.components set from storage your_namespace:items all.raw_super_iron.components

# Get item count in every case
execute store result entity @s Item.count byte 1 run scoreboard players get #item_count your_namespace.data

