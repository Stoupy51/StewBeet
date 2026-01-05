
#> _your_namespace:v3.0.0/load/resolve
#
# @within	#_your_namespace:resolve
#

# If correct version, load the datapack
execute if score #_your_namespace.major load.status matches 3 if score #_your_namespace.minor load.status matches 0 if score #_your_namespace.patch load.status matches 0 run function _your_namespace:v3.0.0/load/main

