
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

# A 1024x1024 logo, cut into a 4x4 grid of glyphs put back together with negative spacing.
# The top tile has to reach the baseline, so the ascent caps the resolution: 32 keeps all 1024px, 128 only 256.
# It hangs 96px below its baseline, hence the trailing lines: they give it room and push it up the chat.
tellraw @a ["===========================>", {"text": "聗聘聙聘聚聘聛聜聝聞聘聟聘聠聘聡聢聝聣聘聤聘聥聘聦聧聝聨聘聩聘聪聘聫聬","font": "_your_namespace:renders"}, "\n\n\n\n\n\n\n\n\n\n\n"]

