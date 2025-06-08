
#> _your_namespace:v2.0.0/minute
#
# @within	_your_namespace:v2.0.0/tick
#

# Reset timer
scoreboard players set #minute _your_namespace.data 1

execute if score #spam _your_namespace.data matches 1 run say This is a message every minute

