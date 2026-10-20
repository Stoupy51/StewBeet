
#> _your_namespace:v3.0.0/second
#
# @within	_your_namespace:v3.0.0/tick
#

# Reset timer
scoreboard players set #second _your_namespace.data 0


# Seats left empty
execute if score #seats _your_namespace.data matches 1.. as @e[type=item_display, tag=_your_namespace.seat] unless predicate {type: "minecraft:entity_properties", entity: "this", predicate: {passenger: {}}} run function _your_namespace:custom_blocks/_interaction/unseat

# 1 second break detection (any custom block)
execute if score #total_custom_blocks _your_namespace.data matches 1.. as @e[type=#_your_namespace:custom_blocks, tag=_your_namespace.custom_block, tag=!_your_namespace.vanilla.minecraft_polished_deepslate, predicate=!_your_namespace:advanced_check_vanilla_blocks] at @s run function _your_namespace:custom_blocks/destroy

# Custom blocks second functions
execute if score #second_entities _your_namespace.data matches 1.. as @e[tag=_your_namespace.second] at @s run function _your_namespace:custom_blocks/second

