
#> _your_namespace:_stats_custom_blocks
#
# @within	???
#

scoreboard players add #tick_entities _your_namespace.data 0
scoreboard players add #second_entities _your_namespace.data 0
scoreboard players add #total_custom_blocks _your_namespace.data 0
scoreboard players add #total_vanilla_raw_iron_block _your_namespace.data 0
scoreboard players add #total_vanilla_polished_deepslate _your_namespace.data 0
scoreboard players add #total_vanilla_iron_block _your_namespace.data 0
scoreboard players add #total_vanilla_cobblestone _your_namespace.data 0
scoreboard players add #total_super_stone _your_namespace.data 0
scoreboard players add #total_raw_steel_block _your_namespace.data 0
scoreboard players add #total_deepslate_steel_ore _your_namespace.data 0
scoreboard players add #total_steel_ore _your_namespace.data 0
scoreboard players add #total_steel_block _your_namespace.data 0
tellraw @s [{"translate": "_your_namespace.total_steel_block","color":"gold"},{"score":{"name":"#total_steel_block","objective":"_your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "_your_namespace.total_steel_ore","color":"gold"},{"score":{"name":"#total_steel_ore","objective":"_your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "_your_namespace.total_deepslate_steel_ore","color":"gold"},{"score":{"name":"#total_deepslate_steel_ore","objective":"_your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "_your_namespace.total_raw_steel_block","color":"gold"},{"score":{"name":"#total_raw_steel_block","objective":"_your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "_your_namespace.total_super_stone","color":"gold"},{"score":{"name":"#total_super_stone","objective":"_your_namespace.data"},"color":"yellow"}]
tellraw @s [{"translate": "_your_namespace.vanilla_minecraft_cobblestone","color":"gray"},{"score":{"name":"#total_vanilla_cobblestone","objective":"_your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "_your_namespace.vanilla_minecraft_iron_block","color":"gray"},{"score":{"name":"#total_vanilla_iron_block","objective":"_your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "_your_namespace.vanilla_minecraft_polished_deepslate","color":"gray"},{"score":{"name":"#total_vanilla_polished_deepslate","objective":"_your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "_your_namespace.vanilla_minecraft_raw_iron_block","color":"gray"},{"score":{"name":"#total_vanilla_raw_iron_block","objective":"_your_namespace.data"},"color":"white"}]
tellraw @s [{"translate": "_your_namespace.total_custom_blocks","color":"dark_aqua"},{"score":{"name":"#total_custom_blocks","objective":"_your_namespace.data"},"color":"aqua"}]
tellraw @s [{"translate": "_your_namespace.second_tag_function","color":"green"},{"score":{"name":"#second_entities","objective":"_your_namespace.data"},"color":"dark_green"}]
tellraw @s [{"translate": "_your_namespace.tick_tag_function","color":"green"},{"score":{"name":"#tick_entities","objective":"_your_namespace.data"},"color":"dark_green"}]

