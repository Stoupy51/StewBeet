
#> _your_namespace:v2.0.0/second_5
#
# @within	_your_namespace:v2.0.0/tick
#

# Reset timer
scoreboard players set #second_5 _your_namespace.data -10

# 5 seconds break detection
execute if score #total_custom_blocks _your_namespace.data matches 1.. as @e[type=item_display,tag=_your_namespace.custom_block,predicate=!_your_namespace:advanced_check_vanilla_blocks] at @s run function _your_namespace:custom_blocks/destroy

execute if score #spam _your_namespace.data matches 1 run say This is a SPAM message every 5 seconds

