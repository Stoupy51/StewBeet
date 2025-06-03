
#> your_namespace:_stats_custom_blocks
#
# @within	???
#

scoreboard players add #total_custom_blocks your_namespace.data 0
scoreboard players add #total_vanilla_raw_iron_block your_namespace.data 0
scoreboard players add #total_vanilla_polished_deepslate your_namespace.data 0
scoreboard players add #total_vanilla_iron_block your_namespace.data 0
scoreboard players add #total_vanilla_cobblestone your_namespace.data 0
scoreboard players add #total_super_stone your_namespace.data 0
scoreboard players add #total_raw_steel_block your_namespace.data 0
scoreboard players add #total_deepslate_steel_ore your_namespace.data 0
scoreboard players add #total_steel_ore your_namespace.data 0
scoreboard players add #total_steel_block your_namespace.data 0
tellraw @s [{"translate": "your_namespace.total_steel_block","color":"gold"},{"score":{"name":"#total_steel_block","objective":"your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "your_namespace.total_steel_ore","color":"gold"},{"score":{"name":"#total_steel_ore","objective":"your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "your_namespace.total_deepslate_steel_ore","color":"gold"},{"score":{"name":"#total_deepslate_steel_ore","objective":"your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "your_namespace.total_raw_steel_block","color":"gold"},{"score":{"name":"#total_raw_steel_block","objective":"your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "your_namespace.total_super_stone","color":"gold"},{"score":{"name":"#total_super_stone","objective":"your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "your_namespace.vanilla_minecraft_cobblestone","color":"gray"},{"score":{"name":"#total_vanilla_cobblestone","objective":"your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "your_namespace.vanilla_minecraft_iron_block","color":"gray"},{"score":{"name":"#total_vanilla_iron_block","objective":"your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "your_namespace.vanilla_minecraft_polished_deepslate","color":"gray"},{"score":{"name":"#total_vanilla_polished_deepslate","objective":"your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "your_namespace.vanilla_minecraft_raw_iron_block","color":"gray"},{"score":{"name":"#total_vanilla_raw_iron_block","objective":"your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "your_namespace.total_custom_blocks","color":"dark_aqua"},{"score":{"name":"#total_custom_blocks","objective":"your_namespace.data"},"color":"aqua"}]

