
#> extensive:test_renders
#
# @within	???
#

tellraw @a [{translate: "_your_namespace.made_of", color: "gray", italic: false}]
tellraw @a ["Steel ingot 16: ", {"text": "聑","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Crafting table: ", {"text": "聒","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Tin ore: ", {render: "mechanization:tin_ore", height: 24, ascent: 12}, "\n\n"]
tellraw @a ["Low res steel ingot: ", {"text": "聓","font": "_your_namespace:renders"}]
tellraw @a ['Like "sprite": ', {"text": "联","font": "_your_namespace:renders"}]
tellraw @a ['This is "sprite": ', {sprite: "_your_namespace:item/steel_ingot", atlas: "minecraft:items"}]
tellraw @a ["Small pack.png: ", {"text": "聕","font": "_your_namespace:renders"}]

# A 1024x1024 logo, cut into a 4x4 grid of glyphs put back together with negative spacing.
# The top tile has to reach the baseline, so the ascent caps the resolution: 32 keeps all 1024px, 128 only 256.
# It hangs 96px below its baseline, hence the trailing lines: they give it room and push it up the chat.
tellraw @a ["===========================>", {render: "stewbeet_logo", height: 128, ascent: 32, resolution: 1024}, "\n\n\n\n\n\n\n\n\n\n\n"]

