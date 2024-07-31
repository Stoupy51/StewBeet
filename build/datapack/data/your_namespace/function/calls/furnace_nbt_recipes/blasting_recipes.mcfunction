
#> your_namespace:calls/furnace_nbt_recipes/blasting_recipes
#
# @within	#furnace_nbt_recipes:v1/blasting_recipes
#

execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"your_namespace": {"raw_super_iron": true}}}} run loot replace block ~ ~ ~ container.3 loot your_namespace:i/super_iron_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"your_namespace": {"super_iron_dust": true}}}} run loot replace block ~ ~ ~ container.3 loot your_namespace:i/super_iron_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"your_namespace": {"super_iron_ore": true}}}} run loot replace block ~ ~ ~ container.3 loot your_namespace:i/super_iron_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"your_namespace": {"deepslate_super_iron_ore": true}}}} run loot replace block ~ ~ ~ container.3 loot your_namespace:i/super_iron_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"your_namespace": {"super_iron_dust": true}}}} run loot replace block ~ ~ ~ container.3 loot your_namespace:i/super_iron_ingot

