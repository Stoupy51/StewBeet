
#> your_namespace:v1.0.0/second_5
#
# @within	your_namespace:v1.0.0/tick
#

# Reset timer
scoreboard players set #second_5 your_namespace.data -10

# 5 seconds break detection
execute as @e[type=item_display,tag=your_namespace.custom_block,predicate=!your_namespace:advanced_check_vanilla_blocks] at @s run function your_namespace:custom_blocks/destroy

