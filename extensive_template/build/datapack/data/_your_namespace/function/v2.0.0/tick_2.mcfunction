
#> _your_namespace:v2.0.0/tick_2
#
# @within	_your_namespace:v2.0.0/tick
#

# Reset timer
scoreboard players set #tick_2 _your_namespace.data 1

# 2 ticks destroy detection
execute if score #total_custom_blocks _your_namespace.data matches 1.. as @e[type=item_display,tag=_your_namespace.custom_block,tag=!_your_namespace.vanilla.minecraft_polished_deepslate,predicate=!_your_namespace:check_vanilla_blocks] at @s run function _your_namespace:custom_blocks/destroy

execute if score #spam _your_namespace.data matches 1 run say This is a SPAM message every 2 ticks

