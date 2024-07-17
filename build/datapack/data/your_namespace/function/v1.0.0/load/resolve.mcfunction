
#> your_namespace:v1.0.0/load/resolve
#
# @within	#your_namespace:resolve
#

# If correct version, load the datapack
execute if score #your_namespace.major load.status matches 1 if score #your_namespace.minor load.status matches 0 if score #your_namespace.patch load.status matches 0 run function your_namespace:v1.0.0/load/main

