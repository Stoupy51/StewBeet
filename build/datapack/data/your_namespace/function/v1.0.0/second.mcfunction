
#> your_namespace:v1.0.0/second
#
# @within	your_namespace:v1.0.0/tick
#

# Reset timer
scoreboard players set #second your_namespace.data 0

# 1 second break detection
execute as @e[type=item_display,tag=your_namespace.custom_block,tag=!your_namespace.vanilla.minecraft_polished_deepslate,predicate=!your_namespace:advanced_check_vanilla_blocks] at @s run function your_namespace:custom_blocks/destroy

