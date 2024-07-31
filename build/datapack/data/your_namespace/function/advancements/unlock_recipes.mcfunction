
#> your_namespace:advancements/unlock_recipes
#
# @within	advancement your_namespace:unlock_recipes
#

# Revoke advancement
advancement revoke @s only your_namespace:unlock_recipes

## For each ingredient in inventory, unlock the recipes
# minecraft:stone
scoreboard players set #success your_namespace.data 0
execute store success score #success your_namespace.data if items entity @s container.* minecraft:stone
execute if score #success your_namespace.data matches 1 run recipe give @s your_namespace:super_stone

# minecraft:deepslate
scoreboard players set #success your_namespace.data 0
execute store success score #success your_namespace.data if items entity @s container.* minecraft:deepslate
execute if score #success your_namespace.data matches 1 run recipe give @s your_namespace:super_stone_2

