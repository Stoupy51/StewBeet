
#> _your_namespace:custom_blocks/lamp/destroy
#
# @executed	as @e[type=item_display,tag=_your_namespace.custom_block,distance=..0.1]
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_light
#

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_light _your_namespace.data 1
scoreboard players remove #total_lamp _your_namespace.data 1

# Kill the custom block entity
kill @s

# Break feedback, the item, and the interaction gone
particle minecraft:item{item: {id: "minecraft:furnace", components: {"minecraft:item_model": "_your_namespace:lamp"}}} ~ ~ ~ 0.25 0.25 0.25 0.1 30
playsound minecraft:block.stone.break block @a ~ ~ ~ 1.0
execute unless score #no_drop _your_namespace.data matches 1 run loot spawn ~ ~ ~ loot _your_namespace:i/lamp
execute positioned ~ ~-0.5 ~ run kill @e[type=interaction, tag=_your_namespace.interaction, distance=..0.01]

