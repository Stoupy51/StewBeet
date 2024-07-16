
#> your_namespace:custom_blocks/super_iron_ore/destroy
#
# @within	your_namespace:custom_blocks/_groups/minecraft_iron_ore
#

# Replace the item with the custom one
execute as @e[type=item,nbt={Item:{id:"minecraft:iron_ore"}},limit=1,sort=nearest,distance=..1] run function your_namespace:custom_blocks/super_iron_ore/replace_item

# Kill the custom block entity
kill @s

