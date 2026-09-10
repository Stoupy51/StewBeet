
#> voltaic:machines/pulverizer/work
#
# @within	voltaic:machines/tick
#			voltaic:machines/pulverizer/slow
#			voltaic:machines/pulverizer/normal
#			voltaic:machines/pulverizer/fast
#

loot replace block ~ ~ ~ container.1 loot voltaic:pulverizer/iron_dust
playsound voltaic:pulverizer block @a[distance=..8]
scoreboard players reset #timer voltaic.data

