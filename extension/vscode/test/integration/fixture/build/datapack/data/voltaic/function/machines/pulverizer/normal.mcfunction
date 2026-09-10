
#> voltaic:machines/pulverizer/normal
#
# @within	???
#

scoreboard players set #interval voltaic.data 10
execute if score #timer voltaic.data matches 10.. run function voltaic:machines/pulverizer/work

