
#> voltaic:gui/smelter/tick
#
# @within	???
#

execute as @a[tag=voltaic.using] run function voltaic:gui/smelter/open
execute as @a[tag=voltaic.watching, tag=!voltaic.using] run function voltaic:gui/smelter/close

