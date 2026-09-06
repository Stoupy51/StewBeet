
#> _your_namespace:v3.0.0/second_5
#
# @within	_your_namespace:v3.0.0/tick
#

# Reset timer
scoreboard players set #second_5 _your_namespace.data -10


# 5 seconds break detection (item display only)
execute if score #total_custom_blocks _your_namespace.data matches 1.. as @e[type=item_display, tag=_your_namespace.custom_block, predicate=!_your_namespace:advanced_check_vanilla_blocks] at @s run function _your_namespace:custom_blocks/destroy

# 5 seconds dynamic brightness update (random sample of item_display custom blocks)
execute if score #total_custom_blocks _your_namespace.data matches 1.. as @e[type=item_display, tag=_your_namespace.custom_block, sort=random, limit=50] at @s run function _your_namespace:custom_blocks/compute_brightness

execute if score #spam _your_namespace.data matches 1 run say This is a SPAM message every 5 seconds

## sourceMappingURL=second_5.mcfunction.map
