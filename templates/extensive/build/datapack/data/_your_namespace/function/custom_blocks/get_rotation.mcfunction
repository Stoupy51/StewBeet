
#> _your_namespace:custom_blocks/get_rotation
#
# @within	???
#

# Set up score
scoreboard players set #rotation _your_namespace.data 0

# Player case
execute if score #rotation _your_namespace.data matches 0 if entity @s[y_rotation=-46..45] run scoreboard players set #rotation _your_namespace.data 1
execute if score #rotation _your_namespace.data matches 0 if entity @s[y_rotation=45..135] run scoreboard players set #rotation _your_namespace.data 2
execute if score #rotation _your_namespace.data matches 0 if entity @s[y_rotation=135..225] run scoreboard players set #rotation _your_namespace.data 3
execute if score #rotation _your_namespace.data matches 0 if entity @s[y_rotation=225..315] run scoreboard players set #rotation _your_namespace.data 4

# Predicate case
execute if score #rotation _your_namespace.data matches 0 if predicate _your_namespace:facing/north run scoreboard players set #rotation _your_namespace.data 1
execute if score #rotation _your_namespace.data matches 0 if predicate _your_namespace:facing/east run scoreboard players set #rotation _your_namespace.data 2
execute if score #rotation _your_namespace.data matches 0 if predicate _your_namespace:facing/south run scoreboard players set #rotation _your_namespace.data 3
execute if score #rotation _your_namespace.data matches 0 if predicate _your_namespace:facing/west run scoreboard players set #rotation _your_namespace.data 4
# No more cases for now

