
#> _your_namespace:calls/furnace_nbt_recipes/blasting_recipes
#
# @within	#furnace_nbt_recipes:v1/blasting_recipes
#

execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"_your_namespace": {"raw_steel": true}}}} run loot replace block ~ ~ ~ container.3 loot _your_namespace:i/steel_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"_your_namespace": {"steel_dust": true}}}} run loot replace block ~ ~ ~ container.3 loot _your_namespace:i/steel_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"_your_namespace": {"steel_ore": true}}}} run loot replace block ~ ~ ~ container.3 loot _your_namespace:i/steel_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"_your_namespace": {"deepslate_steel_ore": true}}}} run loot replace block ~ ~ ~ container.3 loot _your_namespace:i/steel_ingot
execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input{"components": {"minecraft:custom_data": {"_your_namespace": {"steel_dust": true}}}} run loot replace block ~ ~ ~ container.3 loot _your_namespace:i/steel_ingot

