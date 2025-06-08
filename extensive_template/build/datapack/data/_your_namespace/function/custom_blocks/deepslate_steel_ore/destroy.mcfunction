
#> _your_namespace:custom_blocks/deepslate_steel_ore/destroy
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#

# Replace the item with the custom one
execute as @n[type=item,nbt={Item:{id:"minecraft:polished_deepslate"}},distance=..1] run function _your_namespace:custom_blocks/deepslate_steel_ore/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_polished_deepslate _your_namespace.data 1
scoreboard players remove #total_deepslate_steel_ore _your_namespace.data 1

# Kill the custom block entity
kill @s

