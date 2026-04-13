
#> _your_namespace:advancements/unlock_recipes
#
# @executed	as the player & at current position
#
# @within	advancement _your_namespace:unlock_recipes
#

# Revoke advancement
advancement revoke @s only _your_namespace:unlock_recipes

## For each ingredient in inventory, unlock the recipes
# minecraft:stone
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:stone
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stone_rod
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stone_stick
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:super_stone

# minecraft:deepslate
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:deepslate
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:super_stone_2

# minecraft:egg
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:egg
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stewbeet_painting

# minecraft:beetroot
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:beetroot
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stewbeet_painting
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stewbeet_painting_2
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stewbeet_painting_3

# minecraft:blue_egg
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:blue_egg
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stewbeet_painting_2

# minecraft:brown_egg
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:brown_egg
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:stewbeet_painting_3

# minecraft:cobblestone
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:cobblestone
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_no_facing

# minecraft:glass
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:glass
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_visual_facing

# minecraft:furnace
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:furnace
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_block_facing
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_block_states

# minecraft:coal
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:coal
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_block_states

# minecraft:item_frame
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:item_frame
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_contents
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_contents_frame
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_contents_player

# minecraft:compass
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:compass
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_contents_player

# minecraft:string
scoreboard players set #success _your_namespace.data 0
execute store success score #success _your_namespace.data if items entity @s container.* minecraft:string
execute if score #success _your_namespace.data matches 1 run recipe give @s _your_namespace:vb_contents_frame

## Add result items
execute if items entity @s container.* *[custom_data~{_your_namespace: {stone_stick: true}}] run recipe give @s _your_namespace:stone_stick
execute if items entity @s container.* *[custom_data~{_your_namespace: {stone_rod: true}}] run recipe give @s _your_namespace:stone_rod
execute if items entity @s container.* *[custom_data~{_your_namespace: {super_stone: true}}] run recipe give @s _your_namespace:super_stone
execute if items entity @s container.* *[custom_data~{_your_namespace: {super_stone: true}}] run recipe give @s _your_namespace:super_stone_2
execute if items entity @s container.* *[custom_data~{_your_namespace: {stewbeet_painting: true}}] run recipe give @s _your_namespace:stewbeet_painting
execute if items entity @s container.* *[custom_data~{_your_namespace: {stewbeet_painting: true}}] run recipe give @s _your_namespace:stewbeet_painting_2
execute if items entity @s container.* *[custom_data~{_your_namespace: {stewbeet_painting: true}}] run recipe give @s _your_namespace:stewbeet_painting_3
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_no_facing: true}}] run recipe give @s _your_namespace:vb_no_facing
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_visual_facing: true}}] run recipe give @s _your_namespace:vb_visual_facing
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_block_facing: true}}] run recipe give @s _your_namespace:vb_block_facing
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_block_states: true}}] run recipe give @s _your_namespace:vb_block_states
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_contents: true}}] run recipe give @s _your_namespace:vb_contents
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_contents_player: true}}] run recipe give @s _your_namespace:vb_contents_player
execute if items entity @s container.* *[custom_data~{_your_namespace: {vb_contents_frame: true}}] run recipe give @s _your_namespace:vb_contents_frame

