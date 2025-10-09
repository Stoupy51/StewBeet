
#> _your_namespace:custom_blocks/place
#
# @within	_your_namespace:custom_blocks/on_place
#

tag @s add _your_namespace.placer
execute if data storage smithed.custom_block:main blockApi{id:"_your_namespace:steel_block"} run function _your_namespace:custom_blocks/steel_block/place_main
execute if data storage smithed.custom_block:main blockApi{id:"_your_namespace:steel_ore"} run function _your_namespace:custom_blocks/steel_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id:"_your_namespace:deepslate_steel_ore"} run function _your_namespace:custom_blocks/deepslate_steel_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id:"_your_namespace:raw_steel_block"} run function _your_namespace:custom_blocks/raw_steel_block/place_main
execute if data storage smithed.custom_block:main blockApi{id:"_your_namespace:super_stone"} run function _your_namespace:custom_blocks/super_stone/place_main
tag @s remove _your_namespace.placer

