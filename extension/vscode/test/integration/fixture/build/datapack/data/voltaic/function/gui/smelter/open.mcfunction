
#> voltaic:gui/smelter/open
#
# @executed	as @a[tag=voltaic.using]
#
# @within	voltaic:gui/smelter/tick [ as @a[tag=voltaic.using] ]
#

playsound minecraft:block.barrel.open block @s ~ ~ ~ 0.6 1.4
data modify entity @s equipment.head set from storage voltaic:gui Icon
tag @s add voltaic.watching

