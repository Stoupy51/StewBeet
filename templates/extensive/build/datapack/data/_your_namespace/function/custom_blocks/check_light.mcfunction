
#> _your_namespace:custom_blocks/check_light
#
# @executed	positioned ~ ~1 ~
#
# @within	_your_namespace:custom_blocks/compute_brightness [ positioned ~ ~1 ~ ]
#			_your_namespace:custom_blocks/compute_brightness [ positioned ~ ~-1 ~ ]
#			_your_namespace:custom_blocks/compute_brightness [ positioned ~1 ~ ~ ]
#			_your_namespace:custom_blocks/compute_brightness [ positioned ~-1 ~ ~ ]
#			_your_namespace:custom_blocks/compute_brightness [ positioned ~ ~ ~1 ]
#			_your_namespace:custom_blocks/compute_brightness [ positioned ~ ~ ~-1 ]
#

# Check light level at current position and update #light if higher
execute if score #light _your_namespace.data matches ..0 if predicate _your_namespace:light/1 run return run scoreboard players set #light _your_namespace.data 1
execute if score #light _your_namespace.data matches ..1 if predicate _your_namespace:light/2 run return run scoreboard players set #light _your_namespace.data 2
execute if score #light _your_namespace.data matches ..2 if predicate _your_namespace:light/3 run return run scoreboard players set #light _your_namespace.data 3
execute if score #light _your_namespace.data matches ..3 if predicate _your_namespace:light/4 run return run scoreboard players set #light _your_namespace.data 4
execute if score #light _your_namespace.data matches ..4 if predicate _your_namespace:light/5 run return run scoreboard players set #light _your_namespace.data 5
execute if score #light _your_namespace.data matches ..5 if predicate _your_namespace:light/6 run return run scoreboard players set #light _your_namespace.data 6
execute if score #light _your_namespace.data matches ..6 if predicate _your_namespace:light/7 run return run scoreboard players set #light _your_namespace.data 7
execute if score #light _your_namespace.data matches ..7 if predicate _your_namespace:light/8 run return run scoreboard players set #light _your_namespace.data 8
execute if score #light _your_namespace.data matches ..8 if predicate _your_namespace:light/9 run return run scoreboard players set #light _your_namespace.data 9
execute if score #light _your_namespace.data matches ..9 if predicate _your_namespace:light/10 run return run scoreboard players set #light _your_namespace.data 10
execute if score #light _your_namespace.data matches ..10 if predicate _your_namespace:light/11 run return run scoreboard players set #light _your_namespace.data 11
execute if score #light _your_namespace.data matches ..11 if predicate _your_namespace:light/12 run return run scoreboard players set #light _your_namespace.data 12
execute if score #light _your_namespace.data matches ..12 if predicate _your_namespace:light/13 run return run scoreboard players set #light _your_namespace.data 13
execute if score #light _your_namespace.data matches ..13 if predicate _your_namespace:light/14 run return run scoreboard players set #light _your_namespace.data 14
execute if score #light _your_namespace.data matches ..14 if predicate _your_namespace:light/15 run return run scoreboard players set #light _your_namespace.data 15

