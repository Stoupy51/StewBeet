
#> _your_namespace:custom_blocks/_groups/minecraft_raw_iron_block
#
# @within	_your_namespace:custom_blocks/destroy
#

execute if score #total_raw_steel_block _your_namespace.data matches 1.. if entity @s[tag=_your_namespace.raw_steel_block] run function _your_namespace:custom_blocks/raw_steel_block/destroy

