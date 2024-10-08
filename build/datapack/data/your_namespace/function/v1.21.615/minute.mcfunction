
#> your_namespace:v1.21.615/minute
#
# @within	your_namespace:v1.21.615/tick
#

# Reset timer
scoreboard players set #minute your_namespace.data 1
execute if score #spam your_namespace.data matches 1 run say This is a message every minute

