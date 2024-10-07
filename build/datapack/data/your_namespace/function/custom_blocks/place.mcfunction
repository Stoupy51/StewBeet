
#> your_namespace:custom_blocks/place
#
# @within	your_namespace:custom_blocks/on_place
#

tag @s add your_namespace.placer
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:steel_block"} run function your_namespace:custom_blocks/steel_block/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:steel_ore"} run function your_namespace:custom_blocks/steel_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:deepslate_steel_ore"} run function your_namespace:custom_blocks/deepslate_steel_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:raw_steel_block"} run function your_namespace:custom_blocks/raw_steel_block/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:super_stone"} run function your_namespace:custom_blocks/super_stone/place_main
tag @s remove your_namespace.placer

