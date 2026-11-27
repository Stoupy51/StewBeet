
#> extensive:test_renders
#
# @within	???
#

tellraw @a [{translate: "_your_namespace.made_of",fallback: "Made of ", color: "gray", italic: false}]
tellraw @a ["Steel ingot 16: ", {"text": "聑","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Crafting table: ", {"text": "聒","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Tin ore: ", {"text": "聓","font": "_your_namespace:renders"}, "\n\n"]
tellraw @a ["Low res steel ingot: ", {"text": "联","font": "_your_namespace:renders"}]
tellraw @a ['Like "sprite": ', {"text": "聕","font": "_your_namespace:renders"}]
tellraw @a ['This is "sprite": ', {sprite: "_your_namespace:item/steel_ingot", atlas: "minecraft:items"}]
tellraw @a ["Small pack.png: ", {"text": "聖","font": "_your_namespace:renders"}]

# A picture of the project instead of an item: a path under textures_folder, ending with .png.
tellraw @a ["Beer picture: ", {"text": "聗","font": "_your_namespace:renders"}]

# offset moves the pen before the picture, offset_after sets where the pen stops, counted from the picture's right edge.
# A negative offset draws the raw steel 12 pixels back, over the ingot, and "end" follows 4 pixels after it.
tellraw @a ["Overlap: ", {"text": "聑","font": "_your_namespace:renders"}, {"text": "聙聘聚","font": "_your_namespace:renders"}, "end"]
# A negative offset_after brings the pen back over the picture, so the text after it is written on top of it.
tellraw @a ["Text over: ", {"text": "聛聜","font": "_your_namespace:renders"}, {translate: "_your_namespace.steel",fallback: "STEEL", color: "red"}]

# A 1024x1024 logo, cut into a 4x4 grid of glyphs put back together with negative spacing.
# The top tile has to reach the baseline, so the ascent caps the resolution: 32 keeps all 1024px, 128 only 256.
# It hangs 96px below its baseline, hence the trailing lines: they give it room and push it up the chat.
tellraw @a ["===========================>", {"text": "聝聞聟聞聠聞聡聢聣聤聞聥聞聦聞聧聨聣聩聞聪聞聫聞聬聭聣聮聞聯聞聰聞聱聲","font": "_your_namespace:renders"}, "\n\n\n\n\n\n\n\n\n\n\n"]

