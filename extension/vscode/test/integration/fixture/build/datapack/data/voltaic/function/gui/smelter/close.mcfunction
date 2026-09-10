
#> voltaic:gui/smelter/close
#
# @executed	as @a[tag=...]
#
# @within	voltaic:gui/smelter/tick [ as @a[tag=...] ]
#

playsound minecraft:block.barrel.close block @s ~ ~ ~ 0.6 1.4
data remove entity @s equipment.head
tag @s remove voltaic.watching

