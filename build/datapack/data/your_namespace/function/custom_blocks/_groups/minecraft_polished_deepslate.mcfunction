
#> your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#
# @within	your_namespace:custom_blocks/destroy
#

execute if entity @s[tag=your_namespace.super_iron_ore] run function your_namespace:custom_blocks/super_iron_ore/destroy
execute if entity @s[tag=your_namespace.deepslate_super_iron_ore] run function your_namespace:custom_blocks/deepslate_super_iron_ore/destroy

