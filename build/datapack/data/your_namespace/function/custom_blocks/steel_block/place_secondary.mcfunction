
#> your_namespace:custom_blocks/steel_block/place_secondary
#
# @within	your_namespace:custom_blocks/steel_block/place_main
#

# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add your_namespace.custom_block
tag @s add your_namespace.steel_block
tag @s add your_namespace.vanilla.minecraft_iron_block

# Add a custom name
data merge entity @s {"CustomName": {"translate": "your_namespace.steel_block","italic": false,"color": "white"}}


# Modify item display entity to match the custom block
item replace entity @s container.0 with minecraft:furnace[item_model="your_namespace:steel_block"]
data modify entity @s transformation.scale set value [1.002f,1.002f,1.002f]
data modify entity @s brightness set value {block:15,sky:15}

