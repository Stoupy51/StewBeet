
#> your_namespace:calls/smart_ore_generation/generate_ores
#
# @within	#smart_ore_generation:v1/signals/generate_ores
#

# Generate Super Iron Ore (x2)
scoreboard players set #dimension smart_ore_generation.data -1
execute if dimension minecraft:overworld run scoreboard players set #dimension smart_ore_generation.data 0
execute if dimension stardust:cavern run scoreboard players set #dimension smart_ore_generation.data 1
execute if dimension some_other:dimension run scoreboard players set #dimension smart_ore_generation.data 2
scoreboard players set #min_height smart_ore_generation.data 0
scoreboard players set #max_height smart_ore_generation.data 50
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/super_iron_ore

# Generate Deepslate Super Iron Ore (x2)
scoreboard players set #dimension smart_ore_generation.data -1
execute if dimension minecraft:overworld run scoreboard players set #dimension smart_ore_generation.data 0
scoreboard players operation #min_height smart_ore_generation.data = _OVERWORLD_BOTTOM smart_ore_generation.data
scoreboard players set #max_height smart_ore_generation.data 0
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore

# Generate Deepslate Super Iron Ore (x8)
scoreboard players set #dimension smart_ore_generation.data -1
execute if dimension stardust:cavern run scoreboard players set #dimension smart_ore_generation.data 0
scoreboard players operation #min_height smart_ore_generation.data = _OVERWORLD_BOTTOM smart_ore_generation.data
scoreboard players set #max_height smart_ore_generation.data 0
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore
execute if score #dimension smart_ore_generation.data matches 0.. run function your_namespace:calls/smart_ore_generation/veins/deepslate_super_iron_ore

