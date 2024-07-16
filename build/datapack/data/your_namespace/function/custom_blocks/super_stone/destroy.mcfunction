
#> your_namespace:custom_blocks/super_stone/destroy
#
# @within	your_namespace:custom_blocks/_groups/minecraft_stone
#

# Replace the item with the custom one
execute as @e[type=item,nbt={Item:{id:"minecraft:stone"}},limit=1,sort=nearest,distance=..1] run function your_namespace:custom_blocks/super_stone/replace_item

# Kill the custom block entity
kill @s

