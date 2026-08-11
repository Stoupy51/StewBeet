
#> extensive:test_renders
#
# @within	???
#

tellraw @a [{translate: "_your_namespace.made_of", color: "gray", italic: false}]
tellraw @a ["Steel ingot 16: ", {"text": "聆","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Crafting table: ", {"text": "聇","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Tin ore: ", {"text": "聈","font": "_your_namespace:renders"}, "\n\n"]
tellraw @a ["Low res steel ingot: ", {"text": "聉","font": "_your_namespace:renders"}]
tellraw @a ['Like "sprite": ', {"text": "聊","font": "_your_namespace:renders"}]
tellraw @a ['This is "sprite": ', {sprite: "_your_namespace:item/steel_ingot", atlas: "minecraft:items"}]
tellraw @a ["Small pack.png: ", {"text": "聋","font": "_your_namespace:renders"}]

# A 1024x1024 logo, cut into a 4x4 grid of glyphs put back together with negative spacing.
# The top tile has to reach the baseline, so the ascent caps the resolution: 32 keeps all 1024px, 128 only 256.
# It hangs 96px below its baseline, hence the trailing lines: they give it room and push it up the chat.
tellraw @a ["===========================>", {"text": "职聍聎聍聏聍聐聑聒聓聍联聍聕聍聖聗聒聘聍聙聍聚聍聛聜聒聝聍聞聍聟聍聠聡","font": "_your_namespace:renders"}, "\n\n\n\n\n\n\n\n\n\n\n"]

