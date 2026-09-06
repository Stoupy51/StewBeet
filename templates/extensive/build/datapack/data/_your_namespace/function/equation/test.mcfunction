
#> _your_namespace:equation/test
#
# @within	???
#

# scoreboard #value _your_namespace.data = 10 + 5 * 2 / 3 % 100
scoreboard players set #value _your_namespace.data 10
scoreboard players operation #value _your_namespace.data += #5 _your_namespace.data
scoreboard players operation #value _your_namespace.data *= #2 _your_namespace.data
scoreboard players operation #value _your_namespace.data /= #3 _your_namespace.data
scoreboard players operation #value _your_namespace.data %= #100 _your_namespace.data
# scoreboard #value2 _your_namespace.data = 20 - 6 + 7 * 8 / 4 % 5
scoreboard players set #value2 _your_namespace.data 20
scoreboard players operation #value2 _your_namespace.data -= #6 _your_namespace.data
scoreboard players operation #value2 _your_namespace.data += #7 _your_namespace.data
scoreboard players operation #value2 _your_namespace.data *= #8 _your_namespace.data
scoreboard players operation #value2 _your_namespace.data /= #4 _your_namespace.data
scoreboard players operation #value2 _your_namespace.data %= #5 _your_namespace.data

## sourceMappingURL=test.mcfunction.map
