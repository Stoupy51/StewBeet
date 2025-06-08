
#> _your_namespace:v2.0.0/tick
#
# @within	???
#

# Custom blocks tick functions
execute if score #tick_entities _your_namespace.data matches 1.. as @e[tag=_your_namespace.tick] at @s run function _your_namespace:custom_blocks/tick

