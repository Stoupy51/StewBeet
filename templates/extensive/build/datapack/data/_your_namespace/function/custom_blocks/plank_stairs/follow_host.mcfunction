
#> _your_namespace:custom_blocks/plank_stairs/follow_host
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/plank_stairs/place_secondary
#			_your_namespace:custom_blocks/plank_stairs/second
#

execute if block ~ ~ ~ minecraft:oak_stairs[shape=straight] unless items entity @s contents *[custom_model_data={strings: ["shape=straight"]}] run data modify entity @s item.components."minecraft:custom_model_data" set value {strings: ["shape=straight"]}
execute if block ~ ~ ~ minecraft:oak_stairs[shape=inner_left] unless items entity @s contents *[custom_model_data={strings: ["shape=inner_left"]}] run data modify entity @s item.components."minecraft:custom_model_data" set value {strings: ["shape=inner_left"]}
execute if block ~ ~ ~ minecraft:oak_stairs[shape=inner_right] unless items entity @s contents *[custom_model_data={strings: ["shape=inner_right"]}] run data modify entity @s item.components."minecraft:custom_model_data" set value {strings: ["shape=inner_right"]}
execute if block ~ ~ ~ minecraft:oak_stairs[shape=outer_left] unless items entity @s contents *[custom_model_data={strings: ["shape=outer_left"]}] run data modify entity @s item.components."minecraft:custom_model_data" set value {strings: ["shape=outer_left"]}
execute if block ~ ~ ~ minecraft:oak_stairs[shape=outer_right] unless items entity @s contents *[custom_model_data={strings: ["shape=outer_right"]}] run data modify entity @s item.components."minecraft:custom_model_data" set value {strings: ["shape=outer_right"]}

