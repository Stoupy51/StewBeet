
#> your_namespace:custom_blocks/super_iron_block/destroy
#
# @within	your_namespace:custom_blocks/_groups/minecraft_iron_block
#

# Replace the item with the custom one
execute as @e[type=item,nbt={Item:{id:"minecraft:iron_block"}},limit=1,sort=nearest,distance=..1] run function your_namespace:custom_blocks/super_iron_block/replace_item

# Kill the custom block entity
kill @s

