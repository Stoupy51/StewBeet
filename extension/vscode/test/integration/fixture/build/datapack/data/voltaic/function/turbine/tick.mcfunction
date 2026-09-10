
#> voltaic:turbine/tick
#
# @within	voltaic:machines/tick
#

execute store result score #height voltaic.data run data get entity @s Pos[1]
execute if score #height voltaic.data matches ..59 run return run function voltaic:turbine/stall
execute if score #height voltaic.data matches 150.. run scoreboard players add @s energy.storage 40
execute if score @s energy.storage > @s energy.capacity run scoreboard players operation @s energy.storage = @s energy.capacity

