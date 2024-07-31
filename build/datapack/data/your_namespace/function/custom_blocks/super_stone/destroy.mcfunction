
#> your_namespace:custom_blocks/super_stone/destroy
#
# @within	your_namespace:custom_blocks/_groups/minecraft_stone
#

# Replace the item with the custom one
execute as @e[type=item,nbt={Item:{id:"minecraft:stone"}},limit=1,sort=nearest,distance=..1] run function your_namespace:custom_blocks/super_stone/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks your_namespace.data 1
scoreboard players remove #total_vanilla_stone your_namespace.data 1
scoreboard players remove #total_super_stone your_namespace.data 1

# Kill the custom block entity
kill @s

