
#> _your_namespace:custom_blocks/plank_stairs/destroy
#
# @executed	as @e[type=item_display,tag=_your_namespace.custom_block,distance=..0.1]
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_oak_stairs
#

# Replace the item with the custom one
execute as @n[type=item, nbt={Item: {id: "minecraft:oak_stairs"}}, distance=..1] run function _your_namespace:custom_blocks/plank_stairs/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_oak_stairs _your_namespace.data 1
scoreboard players remove #total_plank_stairs _your_namespace.data 1

# Kill the custom block entity
kill @s

# Decrease the number of entities with second tag
scoreboard players remove #second_entities _your_namespace.data 1

