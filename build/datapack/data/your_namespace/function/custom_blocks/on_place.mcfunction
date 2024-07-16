
#> your_namespace:custom_blocks/on_place
#
# @within	#smithed.custom_block:event/on_place
#

execute if data storage smithed.custom_block:main blockApi.__data.Items[0].components."minecraft:custom_data".smithed.block{from:"your_namespace"} run function your_namespace:custom_blocks/place

