
#> _your_namespace:custom_blocks/compute_brightness
#
# @executed	at @s
#
# @within	_your_namespace:custom_blocks/steel_block/place_secondary
#			_your_namespace:custom_blocks/steel_ore/place_secondary
#			_your_namespace:custom_blocks/deepslate_steel_ore/place_secondary
#			_your_namespace:custom_blocks/raw_steel_block/place_secondary
#			_your_namespace:custom_blocks/super_stone/place_secondary
#			_your_namespace:custom_blocks/vb_no_facing/place_secondary
#			_your_namespace:custom_blocks/vb_visual_facing/place_secondary
#			_your_namespace:custom_blocks/vb_block_facing/place_secondary
#			_your_namespace:custom_blocks/vb_block_states/place_secondary
#			_your_namespace:v3.0.0/second_5 [ as @e[type=item_display,tag=_your_namespace.custom_block,sort=random,limit=50] & at @s ]
#

# Reset light score
scoreboard players set #light _your_namespace.data 0

# Check all 6 neighboring positions
execute if score #light _your_namespace.data matches ..14 positioned ~ ~1 ~ run function _your_namespace:custom_blocks/check_light
execute if score #light _your_namespace.data matches ..14 positioned ~ ~-1 ~ run function _your_namespace:custom_blocks/check_light
execute if score #light _your_namespace.data matches ..14 positioned ~1 ~ ~ run function _your_namespace:custom_blocks/check_light
execute if score #light _your_namespace.data matches ..14 positioned ~-1 ~ ~ run function _your_namespace:custom_blocks/check_light
execute if score #light _your_namespace.data matches ..14 positioned ~ ~ ~1 run function _your_namespace:custom_blocks/check_light
execute if score #light _your_namespace.data matches ..14 positioned ~ ~ ~-1 run function _your_namespace:custom_blocks/check_light

# Apply computed brightness to the entity
data merge entity @s {brightness: {block: 0, sky: 0}}
execute store result entity @s brightness.block int 1 run scoreboard players get #light _your_namespace.data
execute store result entity @s brightness.sky int 1 run scoreboard players get #light _your_namespace.data

