
#> your_namespace:custom_blocks/deepslate_super_iron_ore/destroy
#
# @within	your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#

# Replace the item with the custom one
execute as @e[type=item,nbt={Item:{id:"minecraft:polished_deepslate"}},limit=1,sort=nearest,distance=..1] run function your_namespace:custom_blocks/deepslate_super_iron_ore/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks your_namespace.data 1
scoreboard players remove #total_vanilla_polished_deepslate your_namespace.data 1
scoreboard players remove #total_deepslate_super_iron_ore your_namespace.data 1

# Kill the custom block entity
kill @s

