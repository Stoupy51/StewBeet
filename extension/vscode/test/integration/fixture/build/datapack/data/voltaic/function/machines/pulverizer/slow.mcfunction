
#> voltaic:machines/pulverizer/slow
#
# @within	???
#

scoreboard players set #interval voltaic.data 20
execute if score #timer voltaic.data matches 20.. run function voltaic:machines/pulverizer/work

