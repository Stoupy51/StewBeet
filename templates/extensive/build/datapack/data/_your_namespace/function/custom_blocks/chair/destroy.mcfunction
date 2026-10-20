
#> _your_namespace:custom_blocks/chair/destroy
#
# @executed	as @e[type=item_display,tag=_your_namespace.custom_block,distance=..0.1]
#
# @within	_your_namespace:custom_blocks/_groups/minecraft_barrier
#

# Decrease count scores
scoreboard players remove #total_custom_blocks _your_namespace.data 1
scoreboard players remove #total_vanilla_barrier _your_namespace.data 1
scoreboard players remove #total_chair _your_namespace.data 1

# Kill the custom block entity
kill @s

# Break feedback, the item, and the interaction gone
particle minecraft:item{item: {id: "minecraft:furnace", components: {"minecraft:item_model": "_your_namespace:chair"}}} ~ ~ ~ 0.25 0.25 0.25 0.1 30
playsound minecraft:block.wood.break block @a ~ ~ ~ 1.0
execute unless score #no_drop _your_namespace.data matches 1 run loot spawn ~ ~ ~ loot _your_namespace:i/chair
execute positioned ~ ~-0.5 ~ run kill @e[type=interaction, tag=_your_namespace.interaction, distance=..0.01]
kill @e[type=item_display, tag=_your_namespace.seat, distance=..0.6]

