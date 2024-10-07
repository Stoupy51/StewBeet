
#> your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#
# @within	your_namespace:custom_blocks/destroy
#

execute if score #total_steel_ore your_namespace.data matches 1.. if entity @s[tag=your_namespace.steel_ore] run function your_namespace:custom_blocks/steel_ore/destroy
execute if score #total_deepslate_steel_ore your_namespace.data matches 1.. if entity @s[tag=your_namespace.deepslate_steel_ore] run function your_namespace:custom_blocks/deepslate_steel_ore/destroy

