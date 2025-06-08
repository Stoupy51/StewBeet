
#> _your_namespace:custom_blocks/raw_steel_block/destroy
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_raw_iron_block
#

# Replace the item with the custom one
execute as @n[type=item,nbt={Item:{id:"minecraft:raw_iron_block"}},distance=..1] run function _your_namespace:custom_blocks/raw_steel_block/replace_item

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_raw_iron_block _your_namespace.data 1
scoreboard players remove #total_raw_steel_block _your_namespace.data 1

# Kill the custom block entity
kill @s

