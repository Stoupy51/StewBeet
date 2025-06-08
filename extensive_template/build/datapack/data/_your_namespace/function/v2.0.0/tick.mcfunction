
#> _your_namespace:v2.0.0/tick
#
# @within	???
#

# Timers
scoreboard players add #tick_2 _your_namespace.data 1
scoreboard players add #second _your_namespace.data 1
scoreboard players add #second_5 _your_namespace.data 1
scoreboard players add #minute _your_namespace.data 1
execute if score #tick_2 _your_namespace.data matches 3.. run function _your_namespace:v2.0.0/tick_2
execute if score #second _your_namespace.data matches 20.. run function _your_namespace:v2.0.0/second
execute if score #second_5 _your_namespace.data matches 90.. run function _your_namespace:v2.0.0/second_5
execute if score #minute _your_namespace.data matches 1200.. run function _your_namespace:v2.0.0/minute

# Custom blocks tick functions
execute if score #tick_entities _your_namespace.data matches 1.. as @e[tag=_your_namespace.tick] at @s run function _your_namespace:custom_blocks/tick

