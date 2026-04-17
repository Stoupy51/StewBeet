
#> _your_namespace:v3.0.0/load/confirm_load
#
# @within	_your_namespace:v3.0.0/load/valid_dependencies
#

# Opening manual detection
scoreboard objectives add _your_namespace.open_manual minecraft.used:minecraft.written_book

# Register the manual to the universal manual
execute unless data storage stewbeet:main universal_manual run data modify storage stewbeet:main universal_manual set value []
data remove storage stewbeet:main universal_manual[{name: "Extensive Template"}]
data modify storage stewbeet:main universal_manual append value {name: "Extensive Template", loot_table: "_your_namespace:i/manual", hover: [{text: ""}, [{translate:"_your_namespace.extensive_template_manual"}, "\n"], {text: "\u1020\\n\\n\\n\\n\\n\\n", font: "_your_namespace:manual", color: "white"}, [{text: "", font: "minecraft:default", color: "black"}, {translate: "_your_namespace.modify_in_beet_yml_the_text_that_will_be_shown_in_this_first_man", color: "#505050"}]]}

# Confirm load
tellraw @a[tag=convention.debug] {translate: "_your_namespace.loaded_extensive_template_v3_0_0", color: "green"}
scoreboard players set #_your_namespace.loaded load.status 1
function _your_namespace:v3.0.0/load/set_items_storage

# Add a message when loading
say Here is a message when loading the datapack, located in `src/link.py`

# Set scoreboard constants for _your_namespace.data
scoreboard players set #2 _your_namespace.data 2
scoreboard players set #3 _your_namespace.data 3
scoreboard players set #4 _your_namespace.data 4
scoreboard players set #5 _your_namespace.data 5
scoreboard players set #6 _your_namespace.data 6
scoreboard players set #7 _your_namespace.data 7
scoreboard players set #8 _your_namespace.data 8
scoreboard players set #100 _your_namespace.data 100

