
#> _your_namespace:v2.0.0/load/tick_verification
#
# @within	#minecraft:tick
#

execute if score #_your_namespace.major load.status matches 2 if score #_your_namespace.minor load.status matches 0 if score #_your_namespace.patch load.status matches 0 run function _your_namespace:v2.0.0/tick

