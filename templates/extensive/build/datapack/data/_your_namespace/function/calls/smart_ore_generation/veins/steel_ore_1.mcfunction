
#> _your_namespace:calls/smart_ore_generation/veins/steel_ore_1
#
# @within	_your_namespace:calls/smart_ore_generation/generate_ores
#

# Try to find a random position adjacent to air in the region to generate the ore
function #smart_ore_generation:v1/slots/random_position

# Cancel the vein unless every vein condition holds at its start
execute at @s unless biome ~ ~ ~ #minecraft:is_badlands run return fail

# Placing Steel Ore patch
execute at @s if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~-0.4 ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~-0.4 ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~-0.4 ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~ ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~ ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~ ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~0.4 ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~0.4 ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~-0.4 ~0.4 ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~-0.4 ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~-0.4 ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~-0.4 ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~ ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~ ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~ ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~0.4 ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~0.4 ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~ ~0.4 ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~-0.4 ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~-0.4 ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~-0.4 ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~ ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~ ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~ ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~0.4 ~-0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~0.4 ~ if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main
execute at @s positioned ~0.4 ~0.4 ~0.4 if block ~ ~1 ~ #minecraft:terracotta if block ~ ~ ~ #_your_namespace:smart_ore_generation/steel_ore_1_provider unless block ~ ~ ~ minecraft:deepslate run function _your_namespace:custom_blocks/steel_ore/place_main

