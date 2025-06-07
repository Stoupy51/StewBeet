
#> _your_namespace:calls/smart_ore_generation/generate_ores
#
# @within	???
#

# Generate Steel Ore (x2)
scoreboard players set #dimension smart_ore_generation.data -1
execute if dimension minecraft:overworld run scoreboard players set #dimension smart_ore_generation.data 0
execute if dimension stardust:cavern run scoreboard players set #dimension smart_ore_generation.data 1
execute if dimension some_other:dimension run scoreboard players set #dimension smart_ore_generation.data 2
scoreboard players set #min_height smart_ore_generation.data 0
scoreboard players set #max_height smart_ore_generation.data 50
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/steel_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/steel_ore

# Generate Deepslate Steel Ore (x2)
scoreboard players set #dimension smart_ore_generation.data -1
execute if dimension minecraft:overworld run scoreboard players set #dimension smart_ore_generation.data 0
scoreboard players operation #min_height smart_ore_generation.data = _OVERWORLD_BOTTOM smart_ore_generation.data
scoreboard players set #max_height smart_ore_generation.data 0
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_0
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_0

# Generate Deepslate Steel Ore (x8)
scoreboard players set #dimension smart_ore_generation.data -1
execute if dimension stardust:cavern run scoreboard players set #dimension smart_ore_generation.data 0
scoreboard players operation #min_height smart_ore_generation.data = _OVERWORLD_BOTTOM smart_ore_generation.data
scoreboard players set #max_height smart_ore_generation.data 0
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1
execute if score #dimension smart_ore_generation.data matches 0.. run function _your_namespace:calls/smart_ore_generation/veins/deepslate_steel_ore_1

