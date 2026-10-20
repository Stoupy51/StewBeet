
#> _your_namespace:equation/test
#
# @within	(public)
#

# scoreboard #value _your_namespace.data = 10 + 5 * 2 / 3 % 100
execute store result score #value _your_namespace.data run compute default integer {type: "floor_mod", left: {type: "floor_div", left: {type: "mul", inputs: [{type: "add", inputs: [10, 5]}, 2]}, right: 3}, right: 100}
# scoreboard #value2 _your_namespace.data = 20 - 6 + 7 * 8 / 4 % 5
execute store result score #value2 _your_namespace.data run compute default integer {type: "floor_mod", left: {type: "floor_div", left: {type: "mul", inputs: [{type: "add", inputs: [{type: "sub", left: 20, right: 6}, 7]}, 8]}, right: 4}, right: 5}

