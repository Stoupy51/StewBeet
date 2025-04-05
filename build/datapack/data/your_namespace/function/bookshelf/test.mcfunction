
#> your_namespace:bookshelf/test
#
# @within	???
#

# Once
scoreboard players set $math.divide.x bs.in 9
scoreboard players set $math.divide.y bs.in 5
function #bs.math:divide
tellraw @a [{"text":"9 / 5 = ", "color": "dark_gray"},{"score":{"name":"$math.divide", "objective": "bs.out"}, "color": "gold"}]

