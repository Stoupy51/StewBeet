
#> _your_namespace:v2.0.0/load/main
#
# @within	_your_namespace:v2.0.0/load/resolve
#

# Avoiding multiple executions of the same load function
execute unless score #_your_namespace.loaded load.status matches 1 run function _your_namespace:v2.0.0/load/secondary

