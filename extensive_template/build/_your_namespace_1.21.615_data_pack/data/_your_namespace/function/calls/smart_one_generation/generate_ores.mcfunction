
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
