
#> _your_namespace:custom_blocks/super_stone/place_main
#
# @within	_your_namespace:custom_blocks/place
#

tag @s add _your_namespace.placer
setblock ~ ~ ~ air
setblock ~ ~ ~ minecraft:cobblestone
execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function _your_namespace:custom_blocks/super_stone/place_secondary
tag @s remove _your_namespace.placer

# Increment count scores
scoreboard players add #total_custom_blocks _your_namespace.data 1
scoreboard players add #total_vanilla_cobblestone _your_namespace.data 1
scoreboard players add #total_super_stone _your_namespace.data 1

