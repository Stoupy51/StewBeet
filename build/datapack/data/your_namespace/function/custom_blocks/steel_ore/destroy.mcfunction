
#> your_namespace:custom_blocks/steel_ore/destroy
#
# @within	your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#

# Replace the item with the custom one
execute as @n[type=item,nbt={Item:{id:"minecraft:polished_deepslate"}},distance=..1] run function your_namespace:custom_blocks/steel_ore/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks your_namespace.data 1
scoreboard players remove #total_vanilla_polished_deepslate your_namespace.data 1
scoreboard players remove #total_steel_ore your_namespace.data 1

# Kill the custom block entity
kill @s

