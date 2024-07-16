
#> your_namespace:custom_blocks/super_stone/place_main
#
# @within	your_namespace:custom_blocks/place
#

tag @s add your_namespace.placer
setblock ~ ~ ~ air
setblock ~ ~ ~ minecraft:stone
execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function your_namespace:custom_blocks/super_stone/place_secondary
tag @s remove your_namespace.placer

