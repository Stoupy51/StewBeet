
#> your_namespace:v1.21.615/tick_2
#
# @within	your_namespace:v1.21.615/tick
#

# Reset timer
scoreboard players set #tick_2 your_namespace.data 1

# 2 ticks destroy detection
execute if score #total_custom_blocks your_namespace.data matches 1.. as @e[type=item_display,tag=your_namespace.custom_block,tag=!your_namespace.vanilla.minecraft_polished_deepslate,predicate=!your_namespace:check_vanilla_blocks] at @s run function your_namespace:custom_blocks/destroy
say This is a message every 2 ticks

