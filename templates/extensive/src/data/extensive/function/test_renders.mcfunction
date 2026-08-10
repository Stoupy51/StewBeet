

tellraw @a [{"text": "Made of ", "color": "gray", "italic": False}]
tellraw @a ["Steel ingot 16: ",{"render": "steel_ingot", "height": 16}, "\n"]
tellraw @a ["Stone: ",{"render": "minecraft:stone"}, "\n"]
tellraw @a ["Tin ore: ",{"render": "mechanization:tin_ore", "height": 24, "ascent": 12}, "\n\n"]
tellraw @a ["Low res steel ingot: ",{"render": "steel_ingot", "height": 16, "resolution": 8}]
tellraw @a ["Like \"sprite\": ",{"render": "steel_ingot", "height": 8, "resolution": 32, "ascent": 8}]
tellraw @a ["This is \"sprite\": ",{"sprite":"_your_namespace:item/steel_ingot","atlas":"minecraft:items"}]

# Finally, the pack icon on the right
tellraw @a ["===========================>",{"render": "ICON","height": 64,"ascent":64}, "\n"]

