
#> extensive:test_renders
#
# @within	???
#

tellraw @a [{translate: "_your_namespace.made_of", color: "gray", italic: false}]
tellraw @a ["Steel ingot 16: ", {"text": "耥","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Crafting table: ", {"text": "耦","font": "_your_namespace:renders"}, "\n"]
tellraw @a ["Tin ore: ", {"text": "耧","font": "_your_namespace:renders"}, "\n\n"]
tellraw @a ["Low res steel ingot: ", {"text": "耨","font": "_your_namespace:renders"}]
tellraw @a ['Like "sprite": ', {"text": "耩","font": "_your_namespace:renders"}]
tellraw @a ['This is "sprite": ', {sprite: "_your_namespace:item/steel_ingot", atlas: "minecraft:items"}]

# Finally, the pack icon on the right
tellraw @a ["===========================>", {"text": "耪","font": "_your_namespace:renders"}, "\n"]

