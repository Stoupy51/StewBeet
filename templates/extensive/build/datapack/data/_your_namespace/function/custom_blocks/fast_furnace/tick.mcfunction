
#> _your_namespace:custom_blocks/fast_furnace/tick
#
# @executed	as @e[tag=_your_namespace.tick] & at @s
#
# @within	_your_namespace:custom_blocks/tick
#

# Cook 2.0 times faster, never reaching the end itself so vanilla still finishes the item
execute unless block ~ ~ ~ minecraft:furnace[lit=true] run return 0
execute store result score #spent _your_namespace.data run data get block ~ ~ ~ cooking_time_spent
execute if score #spent _your_namespace.data matches 0 run return 0
execute store result score #total _your_namespace.data run data get block ~ ~ ~ cooking_total_time
scoreboard players add #spent _your_namespace.data 1

execute if score #spent _your_namespace.data >= #total _your_namespace.data run scoreboard players operation #spent _your_namespace.data = #total _your_namespace.data
execute if score #spent _your_namespace.data = #total _your_namespace.data run scoreboard players remove #spent _your_namespace.data 1
execute store result block ~ ~ ~ cooking_time_spent int 1 run scoreboard players get #spent _your_namespace.data

