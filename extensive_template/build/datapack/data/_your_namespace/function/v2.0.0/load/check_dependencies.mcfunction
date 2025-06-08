
#> _your_namespace:v2.0.0/load/check_dependencies
#
# @within	_your_namespace:v2.0.0/load/secondary
#

## Check if StewBeet Extensive Template is loadable (dependencies)
scoreboard players set #dependency_error _your_namespace.data 0
execute if score #dependency_error _your_namespace.data matches 0 unless score #common_signals.major load.status matches 0.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 if score #common_signals.major load.status matches 0 unless score #common_signals.minor load.status matches 1.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 unless score #smithed.custom_block.major load.status matches 0.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 if score #smithed.custom_block.major load.status matches 0 unless score #smithed.custom_block.minor load.status matches 7.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 unless score #smart_ore_generation.major load.status matches 1.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 if score #smart_ore_generation.major load.status matches 1 unless score #smart_ore_generation.minor load.status matches 7.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 if score #smart_ore_generation.major load.status matches 1 if score #smart_ore_generation.minor load.status matches 7 unless score #smart_ore_generation.patch load.status matches 1.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 unless score $bs.math.major load.status matches 3.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 if score $bs.math.major load.status matches 3 unless score $bs.math.minor load.status matches 0.. run scoreboard players set #dependency_error _your_namespace.data 1
execute if score #dependency_error _your_namespace.data matches 0 if score $bs.math.major load.status matches 3 if score $bs.math.minor load.status matches 0 unless score $bs.math.patch load.status matches 2.. run scoreboard players set #dependency_error _your_namespace.data 1

