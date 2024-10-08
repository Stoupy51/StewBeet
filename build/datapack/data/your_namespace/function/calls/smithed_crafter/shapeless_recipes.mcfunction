
#> your_namespace:calls/smithed_crafter/shapeless_recipes
#
# @within	#smithed.crafter:event/shapeless_recipes
#

execute if score @s smithed.data matches 0 store result score @s smithed.data if score count smithed.data matches 1 if data storage smithed.crafter:input {"recipe": [{"count": 1, "components": {"minecraft:custom_data": {"your_namespace": {"steel_block": true}}}}]} run loot replace block ~ ~ ~ container.16 loot your_namespace:i/steel_ingot_x9
execute if score @s smithed.data matches 0 store result score @s smithed.data if score count smithed.data matches 1 if data storage smithed.crafter:input {"recipe": [{"count": 1, "components": {"minecraft:custom_data": {"your_namespace": {"steel_ingot": true}}}}]} run loot replace block ~ ~ ~ container.16 loot your_namespace:i/steel_nugget_x9
execute if score @s smithed.data matches 0 store result score @s smithed.data if score count smithed.data matches 1 if data storage smithed.crafter:input {"recipe": [{"id": "minecraft:deepslate", "count": 9}]} run loot replace block ~ ~ ~ container.16 loot your_namespace:i/super_stone

