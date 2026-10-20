
#> _your_namespace:custom_blocks/ruby_ore/replace_item
#
# @executed	as @n[type=item,nbt={Item:{id:"minecraft:polished_deepslate"}},distance=..1]
#
# @within	_your_namespace:custom_blocks/ruby_ore/destroy [ as @n[type=item,nbt={Item:{id:"minecraft:polished_deepslate"}},distance=..1] ]
#

# Mined with a tool too weak
execute if entity @p[distance=..8, gamemode=!creative, gamemode=!spectator] unless items entity @p[distance=..8, gamemode=!creative, gamemode=!spectator] weapon.mainhand #_your_namespace:mining/pickaxe_iron run return run kill @s


# If silk touch applied
execute if score #is_silk_touch _your_namespace.data matches 1 run data modify entity @s Item.id set from storage _your_namespace:items all.ruby_ore.id
execute if score #is_silk_touch _your_namespace.data matches 1 run data modify entity @s Item.components set from storage _your_namespace:items all.ruby_ore.components

# Else, no silk touch
execute if score #is_silk_touch _your_namespace.data matches 0 positioned ~ ~ ~ as @p[distance=..10, gamemode=!spectator] run loot spawn ~ ~ ~ fish _your_namespace:custom_blocks/no_silk_touch_drop/ruby_ore ~ ~ ~ mainhand
execute if score #is_silk_touch _your_namespace.data matches 0 unless entity @p[distance=..10, gamemode=!spectator] run loot spawn ~ ~ ~ loot _your_namespace:custom_blocks/no_silk_touch_drop/ruby_ore
execute if score #is_silk_touch _your_namespace.data matches 0 run kill @s
execute if score #is_silk_touch _your_namespace.data matches 0 summon minecraft:experience_orb store result entity @s Value short 1 run random value 2..4

# Keep item count when silk touch is applied
execute if score #is_silk_touch _your_namespace.data matches 1 store result entity @s Item.count byte 1 run scoreboard players get #item_count _your_namespace.data

