
#> your_namespace:custom_blocks/deepslate_steel_ore/place_main
#
# @within	your_namespace:custom_blocks/place
#			your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore
#

tag @s add your_namespace.placer
setblock ~ ~ ~ air
setblock ~ ~ ~ minecraft:polished_deepslate
execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function your_namespace:custom_blocks/deepslate_steel_ore/place_secondary
tag @s remove your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks your_namespace.data 1
scoreboard players add #total_vanilla_polished_deepslate your_namespace.data 1
scoreboard players add #total_deepslate_steel_ore your_namespace.data 1

