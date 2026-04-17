
#> _your_namespace:custom_blocks/raw_steel_block/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:raw_iron_block"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/raw_steel_block/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:raw_iron_block"}},distance=..1] ]
#

# If silk touch applied
execute if score #is_silk_touch _your_namespace.data matches 1 run data modify entity @s Item.id set from storage _your_namespace:items all.raw_steel_block.id
execute if score #is_silk_touch _your_namespace.data matches 1 run data modify entity @s Item.components set from storage _your_namespace:items all.raw_steel_block.components

# Else, no silk touch
execute if score #is_silk_touch _your_namespace.data matches 0 positioned ~ ~ ~ as @p[distance=..10, gamemode=!spectator] run loot spawn ~ ~ ~ fish _your_namespace:custom_blocks/no_silk_touch_drop/raw_steel_block ~ ~ ~ mainhand
execute if score #is_silk_touch _your_namespace.data matches 0 unless entity @p[distance=..10, gamemode=!spectator] run loot spawn ~ ~ ~ loot _your_namespace:custom_blocks/no_silk_touch_drop/raw_steel_block
execute if score #is_silk_touch _your_namespace.data matches 0 run kill @s

