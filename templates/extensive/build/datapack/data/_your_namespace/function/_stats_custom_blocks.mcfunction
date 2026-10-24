
#> _your_namespace:_stats_custom_blocks
#
# @within	(public)
#

scoreboard players add #second_entities _your_namespace.data 0
scoreboard players add #tick_entities _your_namespace.data 0
scoreboard players add #total_custom_blocks _your_namespace.data 0
scoreboard players add #total_vanilla_item_frame _your_namespace.data 0
scoreboard players add #total_vanilla_raw_iron_block _your_namespace.data 0
scoreboard players add #total_vanilla_polished_deepslate _your_namespace.data 0
scoreboard players add #total_vanilla_oak_stairs _your_namespace.data 0
scoreboard players add #total_vanilla_oak_slab _your_namespace.data 0
scoreboard players add #total_vanilla_light _your_namespace.data 0
scoreboard players add #total_vanilla_iron_block _your_namespace.data 0
scoreboard players add #total_vanilla_glass _your_namespace.data 0
scoreboard players add #total_vanilla_furnace _your_namespace.data 0
scoreboard players add #total_vanilla_diamond_block _your_namespace.data 0
scoreboard players add #total_vanilla_cobblestone _your_namespace.data 0
scoreboard players add #total_vanilla_barrier _your_namespace.data 0
scoreboard players add #total_lamp _your_namespace.data 0
scoreboard players add #total_ruby_ore _your_namespace.data 0
scoreboard players add #total_fast_furnace _your_namespace.data 0
scoreboard players add #total_plank_stairs _your_namespace.data 0
scoreboard players add #total_plank_slab _your_namespace.data 0
scoreboard players add #total_crate _your_namespace.data 0
scoreboard players add #total_chair _your_namespace.data 0
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

tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_steel_block",fallback: "Total 'Steel Block'"}, ": "], {score: {name: "#total_steel_block", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_steel_ore",fallback: "Total 'Steel Ore'"}, ": "], {score: {name: "#total_steel_ore", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_deepslate_steel_ore",fallback: "Total 'Deepslate Steel Ore'"}, ": "], {score: {name: "#total_deepslate_steel_ore", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_raw_steel_block",fallback: "Total 'Raw Steel Block'"}, ": "], {score: {name: "#total_raw_steel_block", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_super_stone",fallback: "Total 'Super Stone'"}, ": "], {score: {name: "#total_super_stone", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_no_facing",fallback: "Total 'Vb No Facing'"}, ": "], {score: {name: "#total_vb_no_facing", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_visual_facing",fallback: "Total 'Vb Visual Facing'"}, ": "], {score: {name: "#total_vb_visual_facing", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_block_facing",fallback: "Total 'Vb Block Facing'"}, ": "], {score: {name: "#total_vb_block_facing", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_block_states",fallback: "Total 'Vb Block States'"}, ": "], {score: {name: "#total_vb_block_states", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_contents",fallback: "Total 'Vb Contents'"}, ": "], {score: {name: "#total_vb_contents", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_contents_player",fallback: "Total 'Vb Contents Player'"}, ": "], {score: {name: "#total_vb_contents_player", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_vb_contents_frame",fallback: "Total 'Vb Contents Frame'"}, ": "], {score: {name: "#total_vb_contents_frame", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_chair",fallback: "Total 'Chair'"}, ": "], {score: {name: "#total_chair", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_crate",fallback: "Total 'Crate'"}, ": "], {score: {name: "#total_crate", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_plank_slab",fallback: "Total 'Plank Slab'"}, ": "], {score: {name: "#total_plank_slab", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_plank_stairs",fallback: "Total 'Plank Stairs'"}, ": "], {score: {name: "#total_plank_stairs", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_fast_furnace",fallback: "Total 'Fast Furnace'"}, ": "], {score: {name: "#total_fast_furnace", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_ruby_ore",fallback: "Total 'Ruby Ore'"}, ": "], {score: {name: "#total_ruby_ore", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gold"}, {translate: "_your_namespace.total_lamp",fallback: "Total 'Lamp'"}, ": "], {score: {name: "#total_lamp", objective: "_your_namespace.data"}, color: "yellow"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_barrier",fallback: "Vanilla 'minecraft:barrier'"}, ": "], {score: {name: "#total_vanilla_barrier", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_cobblestone",fallback: "Vanilla 'minecraft:cobblestone'"}, ": "], {score: {name: "#total_vanilla_cobblestone", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_diamond_block",fallback: "Vanilla 'minecraft:diamond_block'"}, ": "], {score: {name: "#total_vanilla_diamond_block", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_furnace",fallback: "Vanilla 'minecraft:furnace'"}, ": "], {score: {name: "#total_vanilla_furnace", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_glass",fallback: "Vanilla 'minecraft:glass'"}, ": "], {score: {name: "#total_vanilla_glass", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_iron_block",fallback: "Vanilla 'minecraft:iron_block'"}, ": "], {score: {name: "#total_vanilla_iron_block", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_light",fallback: "Vanilla 'minecraft:light'"}, ": "], {score: {name: "#total_vanilla_light", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_oak_slab",fallback: "Vanilla 'minecraft:oak_slab'"}, ": "], {score: {name: "#total_vanilla_oak_slab", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_oak_stairs",fallback: "Vanilla 'minecraft:oak_stairs'"}, ": "], {score: {name: "#total_vanilla_oak_stairs", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_polished_deepslate",fallback: "Vanilla 'minecraft:polished_deepslate'"}, ": "], {score: {name: "#total_vanilla_polished_deepslate", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_raw_iron_block",fallback: "Vanilla 'minecraft:raw_iron_block'"}, ": "], {score: {name: "#total_vanilla_raw_iron_block", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "gray"}, {translate: "_your_namespace.vanilla_minecraft_item_frame",fallback: "Vanilla 'minecraft:item_frame'"}, ": "], {score: {name: "#total_vanilla_item_frame", objective: "_your_namespace.data"}, color: "white"}]
tellraw @s [[{text:"- ", color: "dark_aqua"}, {translate: "_your_namespace.total_custom_blocks",fallback: "Total custom blocks: "}], {score: {name: "#total_custom_blocks", objective: "_your_namespace.data"}, color: "aqua"}]
tellraw @s [[{"text":"- ","color":"green"}, {"translate":"_your_namespace.tick_tag_function","fallback":"'tick' tag function: "}],{"score":{"name":"#tick_entities","objective":"_your_namespace.data"},"color":"dark_green"}]
tellraw @s [[{"text":"- ","color":"green"}, {"translate":"_your_namespace.second_tag_function","fallback":"'second' tag function: "}],{"score":{"name":"#second_entities","objective":"_your_namespace.data"},"color":"dark_green"}]

