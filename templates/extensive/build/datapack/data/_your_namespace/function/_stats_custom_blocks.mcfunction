
#> _your_namespace:_stats_custom_blocks
#
# @within	???
#

scoreboard players add #second_entities _your_namespace.data 0
scoreboard players add #tick_entities _your_namespace.data 0
scoreboard players add #total_custom_blocks _your_namespace.data 0
scoreboard players add #total_vanilla_item_frame _your_namespace.data 0
scoreboard players add #total_vanilla_raw_iron_block _your_namespace.data 0
scoreboard players add #total_vanilla_polished_deepslate _your_namespace.data 0
scoreboard players add #total_vanilla_iron_block _your_namespace.data 0
scoreboard players add #total_vanilla_glass _your_namespace.data 0
scoreboard players add #total_vanilla_furnace _your_namespace.data 0
scoreboard players add #total_vanilla_cobblestone _your_namespace.data 0
scoreboard players add #total_vb_contents_frame _your_namespace.data 0
scoreboard players add #total_vb_contents_player _your_namespace.data 0
scoreboard players add #total_vb_contents _your_namespace.data 0
scoreboard players add #total_vb_block_states _your_namespace.data 0
scoreboard players add #total_vb_block_facing _your_namespace.data 0
scoreboard players add #total_vb_visual_facing _your_namespace.data 0
scoreboard players add #total_vb_no_facing _your_namespace.data 0
scoreboard players add #total_super_stone _your_namespace.data 0
scoreboard players add #total_raw_steel_block _your_namespace.data 0
scoreboard players add #total_deepslate_steel_ore _your_namespace.data 0
scoreboard players add #total_steel_ore _your_namespace.data 0
scoreboard players add #total_steel_block _your_namespace.data 0

tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_steel_block"}, ": "], {score: {name: "#total_steel_block", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_steel_ore"}, ": "], {score: {name: "#total_steel_ore", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_deepslate_steel_ore"}, ": "], {score: {name: "#total_deepslate_steel_ore", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_raw_steel_block"}, ": "], {score: {name: "#total_raw_steel_block", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_super_stone"}, ": "], {score: {name: "#total_super_stone", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_no_facing"}, ": "], {score: {name: "#total_vb_no_facing", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_visual_facing"}, ": "], {score: {name: "#total_vb_visual_facing", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_block_facing"}, ": "], {score: {name: "#total_vb_block_facing", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_block_states"}, ": "], {score: {name: "#total_vb_block_states", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_contents"}, ": "], {score: {name: "#total_vb_contents", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_contents_player"}, ": "], {score: {name: "#total_vb_contents_player", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_contents_frame"}, ": "], {score: {name: "#total_vb_contents_frame", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_cobblestone"}, ": "], {score: {name: "#total_vanilla_cobblestone", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_furnace"}, ": "], {score: {name: "#total_vanilla_furnace", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_glass"}, ": "], {score: {name: "#total_vanilla_glass", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_iron_block"}, ": "], {score: {name: "#total_vanilla_iron_block", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_polished_deepslate"}, ": "], {score: {name: "#total_vanilla_polished_deepslate", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_raw_iron_block"}, ": "], {score: {name: "#total_vanilla_raw_iron_block", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_item_frame"}, ": "], {score: {name: "#total_vanilla_item_frame", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "dark_aqua"}, {translate: "_your_namespace.total_custom_blocks"}], {score: {name: "#total_custom_blocks", objective: "_your_namespace.data"}, color: "aqua"}]
tellraw @s [[{"text":"- ","color":"green"}, {"translate":"_your_namespace.tick_tag_function"}],{"score":{"name":"#tick_entities","objective":"_your_namespace.data"},"color":"dark_green"}]
tellraw @s [[{"text":"- ","color":"green"}, {"translate":"_your_namespace.second_tag_function"}],{"score":{"name":"#second_entities","objective":"_your_namespace.data"},"color":"dark_green"}]

## sourceMappingURL=_stats_custom_blocks.mcfunction.map
