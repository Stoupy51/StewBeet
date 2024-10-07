
#> your_namespace:v1.21.615/load/tick_verification
#
# @within	#minecraft:tick
#

execute if score #your_namespace.major load.status matches 1 if score #your_namespace.minor load.status matches 21 if score #your_namespace.patch load.status matches 615 run function your_namespace:v1.21.615/tick

