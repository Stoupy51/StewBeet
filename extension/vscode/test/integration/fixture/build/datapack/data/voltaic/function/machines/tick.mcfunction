
#> voltaic:machines/tick
#
# @within	???
#

execute unless score @s energy.storage >= @s voltaic.energy_rate run return fail
scoreboard players operation @s energy.storage -= @s voltaic.energy_rate
execute if entity @s[tag=voltaic.turbine] run function voltaic:turbine/tick
function voltaic:machines/pulverizer/work

