
#> _your_namespace:v3.0.0/load/confirm_load
#
# @within	_your_namespace:v3.0.0/load/valid_dependencies
#

# Opening manual detection
scoreboard objectives add _your_namespace.open_manual minecraft.used:minecraft.written_book


# Confirm load
tellraw @a[tag=convention.debug] {translate: "_your_namespace.loaded_extensive_template_v3_0_0",fallback: "[Loaded Extensive Template v3.0.0]", color: "green"}
scoreboard players set #_your_namespace.loaded load.status 1
function _your_namespace:v3.0.0/load/set_items_storage

# Hits of interaction blocks
scoreboard objectives add _your_namespace.hits dummy
scoreboard objectives add _your_namespace.last_hit dummy

# Add a message when loading
tellraw @a ["Here is a message when loading the datapack, located in `src/link.py`\n\n\n"]
tellraw @a [{"text": "聏","font": "_your_namespace:renders"}, {"text": "聐","font": "_your_namespace:renders"}, "\n\n\n\n"]

