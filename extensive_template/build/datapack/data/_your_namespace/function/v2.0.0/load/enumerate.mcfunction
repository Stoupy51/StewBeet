
#> _your_namespace:v2.0.0/load/enumerate
#
# @within	#_your_namespace:enumerate
#

# If current major is too low, set it to the current major
execute unless score #_your_namespace.major load.status matches 2.. run scoreboard players set #_your_namespace.major load.status 2

# If current minor is too low, set it to the current minor (only if major is correct)
execute if score #_your_namespace.major load.status matches 2 unless score #_your_namespace.minor load.status matches 0.. run scoreboard players set #_your_namespace.minor load.status 0

# If current patch is too low, set it to the current patch (only if major and minor are correct)
execute if score #_your_namespace.major load.status matches 2 if score #_your_namespace.minor load.status matches 0 unless score #_your_namespace.patch load.status matches 0.. run scoreboard players set #_your_namespace.patch load.status 0

