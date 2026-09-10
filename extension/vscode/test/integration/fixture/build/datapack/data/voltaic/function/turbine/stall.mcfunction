
#> voltaic:turbine/stall
#
# @within	voltaic:turbine/tick
#

data modify entity @s item.components."minecraft:item_model" set value "voltaic:turbine_stalled"
stopsound @a[distance=..16] ambient voltaic:turbine

