
#> _your_namespace:custom_blocks/_groups/minecraft_polished_deepslate
#
# @within	_your_namespace:custom_blocks/destroy
#

execute if score #total_steel_ore _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.steel_ore] run function _your_namespace:custom_blocks/steel_ore/destroy
execute if score #total_deepslate_steel_ore _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.deepslate_steel_ore] run function _your_namespace:custom_blocks/deepslate_steel_ore/destroy

