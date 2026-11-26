
tellraw @a [{"text": "Made of ", "color": "gray", "italic": False}]
tellraw @a ["Steel ingot 16: ",{"render": "steel_ingot", "height": 16}, "\n"]
tellraw @a ["Crafting table: ",{"render": "minecraft:crafting_table"}, "\n"]
tellraw @a ["Tin ore: ",{"render": "mechanization:tin_ore", "height": 24, "ascent": 12}, "\n\n"]
tellraw @a ["Low res steel ingot: ",{"render": "steel_ingot", "height": 16, "resolution": 8}]
tellraw @a ["Like \"sprite\": ",{"render": "steel_ingot", "height": 8, "resolution": 32, "ascent": 8}]
tellraw @a ["This is \"sprite\": ",{"sprite":"_your_namespace:item/steel_ingot","atlas":"minecraft:items"}]
tellraw @a ["Small pack.png: ",{"render": "ICON", "height": 8, "ascent": 8}]

# A picture of the project instead of an item: a path under textures_folder, ending with .png.
tellraw @a ["Beer picture: ",{"render": "beer.png", "height": 16}]

# offset moves the pen before the picture, offset_after sets where the pen stops, counted from the picture's right edge.
# A negative offset draws the raw steel 12 pixels back, over the ingot, and "end" follows 4 pixels after it.
tellraw @a ["Overlap: ",{"render": "steel_ingot", "height": 16},{"render": "raw_steel", "height": 16, "offset": -12, "offset_after": 4},"end"]
# A negative offset_after brings the pen back over the picture, so the text after it is written on top of it.
tellraw @a ["Text over: ",{"render": "steel_block", "height": 16, "offset_after": -16},{"text": "STEEL", "color": "red"}]

# A 1024x1024 logo, cut into a 4x4 grid of glyphs put back together with negative spacing.
# The top tile has to reach the baseline, so the ascent caps the resolution: 32 keeps all 1024px, 128 only 256.
# It hangs 96px below its baseline, hence the trailing lines: they give it room and push it up the chat.
tellraw @a ["===========================>",{"render": "stewbeet:logo", "height": 128, "ascent": 32, "resolution": 1024}, "\n\n\n\n\n\n\n\n\n\n\n"]

