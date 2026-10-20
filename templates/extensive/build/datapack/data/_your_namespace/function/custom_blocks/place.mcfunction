
#> _your_namespace:custom_blocks/place
#
# @within	_your_namespace:custom_blocks/on_place
#

tag @s add _your_namespace.placer
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:steel_block"} run function _your_namespace:custom_blocks/steel_block/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:steel_ore"} run function _your_namespace:custom_blocks/steel_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:deepslate_steel_ore"} run function _your_namespace:custom_blocks/deepslate_steel_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:raw_steel_block"} run function _your_namespace:custom_blocks/raw_steel_block/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:super_stone"} run function _your_namespace:custom_blocks/super_stone/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:vb_no_facing"} run function _your_namespace:custom_blocks/vb_no_facing/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:vb_visual_facing"} run function _your_namespace:custom_blocks/vb_visual_facing/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:vb_block_facing"} run function _your_namespace:custom_blocks/vb_block_facing/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:vb_block_states"} run function _your_namespace:custom_blocks/vb_block_states/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:chair"} run function _your_namespace:custom_blocks/chair/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:crate"} run function _your_namespace:custom_blocks/crate/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:plank_slab"} run function _your_namespace:custom_blocks/plank_slab/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:plank_stairs"} run function _your_namespace:custom_blocks/plank_stairs/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:fast_furnace"} run function _your_namespace:custom_blocks/fast_furnace/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:ruby_ore"} run function _your_namespace:custom_blocks/ruby_ore/place_main
execute if data storage smithed.custom_block:main blockApi{id: "_your_namespace:lamp"} run function _your_namespace:custom_blocks/lamp/place_main
tag @s remove _your_namespace.placer

