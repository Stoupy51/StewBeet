
#> voltaic:gui/pulverizer/tick
#
# @within	???
#

execute as @a[tag=voltaic.using] run function voltaic:gui/pulverizer/open
execute as @a[tag=voltaic.watching, tag=!voltaic.using] run function voltaic:gui/pulverizer/close

