
#> your_namespace:custom_blocks/super_iron_ore/place_main
#
# @within	your_namespace:custom_blocks/place
#			your_namespace:calls/smart_ore_generation/veins/super_iron_ore
#

tag @s add your_namespace.placer
setblock ~ ~ ~ air
setblock ~ ~ ~ minecraft:polished_deepslate
execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function your_namespace:custom_blocks/super_iron_ore/place_secondary
tag @s remove your_namespace.placer

