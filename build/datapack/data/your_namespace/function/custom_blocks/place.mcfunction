
#> your_namespace:custom_blocks/place
#
# @within	your_namespace:custom_blocks/on_place
#

tag @s add your_namespace.placer
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:super_iron_block"} run function your_namespace:custom_blocks/super_iron_block/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:super_iron_ore"} run function your_namespace:custom_blocks/super_iron_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:deepslate_super_iron_ore"} run function your_namespace:custom_blocks/deepslate_super_iron_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:raw_super_iron_block"} run function your_namespace:custom_blocks/raw_super_iron_block/place_main
execute if data storage smithed.custom_block:main blockApi{id:"your_namespace:super_stone"} run function your_namespace:custom_blocks/super_stone/place_main
tag @s remove your_namespace.placer

