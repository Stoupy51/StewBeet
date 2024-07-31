
#> your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#
# @within	your_namespace:custom_blocks/destroy
#

execute if score #total_super_iron_ore your_namespace.data matches 1.. if entity @s[tag=your_namespace.super_iron_ore] run function your_namespace:custom_blocks/super_iron_ore/destroy
execute if score #total_deepslate_super_iron_ore your_namespace.data matches 1.. if entity @s[tag=your_namespace.deepslate_super_iron_ore] run function your_namespace:custom_blocks/deepslate_super_iron_ore/destroy

