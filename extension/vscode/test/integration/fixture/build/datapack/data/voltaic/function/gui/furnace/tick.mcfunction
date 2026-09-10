
#> voltaic:gui/furnace/tick
#
# @within	???
#

execute as @a[tag=voltaic.using] run function voltaic:gui/furnace/open
execute as @a[tag=voltaic.watching, tag=!voltaic.using] run function voltaic:gui/furnace/close

