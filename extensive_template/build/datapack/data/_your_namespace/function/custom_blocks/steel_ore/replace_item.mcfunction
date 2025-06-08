
#> _your_namespace:custom_blocks/steel_ore/replace_item
#
# @within	_your_namespace:custom_blocks/steel_ore/destroy
#

# If silk touch applied
execute if score #is_silk_touch _your_namespace.data matches 1 run data modify entity @s Item.id set from storage _your_namespace:items all.steel_ore.id
execute if score #is_silk_touch _your_namespace.data matches 1 run data modify entity @s Item.components set from storage _your_namespace:items all.steel_ore.components

# Else, no silk touch
execute if score #is_silk_touch _your_namespace.data matches 0 run data modify entity @s Item.id set from storage _your_namespace:items all.raw_steel.id
execute if score #is_silk_touch _your_namespace.data matches 0 run data modify entity @s Item.components set from storage _your_namespace:items all.raw_steel.components

# Get item count in every case
execute store result entity @s Item.count byte 1 run scoreboard players get #item_count _your_namespace.data

