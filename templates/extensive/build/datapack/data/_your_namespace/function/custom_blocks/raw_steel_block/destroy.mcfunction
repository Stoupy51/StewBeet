
#> _your_namespace:custom_blocks/raw_steel_block/destroy
#
# @executed	as @e[type=item_display,tag=...,predicate=!_your_namespace:check_vanilla_blocks] & at @s
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_raw_iron_block
#

# Check if the player has silk touch in mainhand
scoreboard players set #is_silk_touch _your_namespace.data 0
execute as @p[distance=..10, gamemode=!spectator] if data entity @s SelectedItem.components."minecraft:enchantments"."minecraft:silk_touch" run scoreboard players set #is_silk_touch _your_namespace.data 1

# If no item found, summon it
execute unless entity @n[type=item, nbt={Item: {id: "minecraft:raw_iron_block"}}, distance=..1] run loot spawn ~ ~ ~ loot {pools: [{entries: [{type: "minecraft:item", name: "minecraft:glass"}], rolls: 1}]}

# Replace the item with the custom one
execute as @n[type=item, nbt={Item: {id: "minecraft:raw_iron_block"}}, distance=..1] run function _your_namespace:custom_blocks/raw_steel_block/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_raw_iron_block _your_namespace.data 1
scoreboard players remove #total_raw_steel_block _your_namespace.data 1

# Kill the custom block entity
kill @s

