

tellraw @a [{"text": "Made of ", "color": "gray", "italic": False}]
tellraw @a ["Steel ingot 16: ",{"render": "steel_ingot", "height": 16}, "\n"]
tellraw @a ["Crafting table: ",{"render": "minecraft:crafting_table"}, "\n"]
tellraw @a ["Tin ore: ",{"render": "mechanization:tin_ore", "height": 24, "ascent": 12}, "\n\n"]
tellraw @a ["Low res steel ingot: ",{"render": "steel_ingot", "height": 16, "resolution": 8}]
tellraw @a ["Like \"sprite\": ",{"render": "steel_ingot", "height": 8, "resolution": 32, "ascent": 8}]
tellraw @a ["This is \"sprite\": ",{"sprite":"_your_namespace:item/steel_ingot","atlas":"minecraft:items"}]
tellraw @a ["Small pack.png: ",{"render": "ICON", "height": 8, "ascent": 8}]

# A 1024x1024 logo, cut into a 4x4 grid of glyphs put back together with negative spacing.
# The top tile has to reach the baseline, so the ascent caps the resolution: 32 keeps all 1024px, 128 only 256.
# It hangs 96px below its baseline, hence the trailing lines: they give it room and push it up the chat.
tellraw @a ["===========================>",{"render": "stewbeet_logo", "height": 128, "ascent": 32, "resolution": 1024}, "\n\n\n\n\n\n\n\n\n\n\n"]

