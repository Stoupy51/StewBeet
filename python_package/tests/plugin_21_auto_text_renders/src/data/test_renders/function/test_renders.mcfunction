

tellraw @a {"text": "Made of ", "color": "gray", "italic": False}
tellraw @a {"render": "steel_ingot", "height": 8}
tellraw @a {"render": "minecraft:stone"}
tellraw @a {"render": "mechanization:tin_ore", "height": 12, "ascent": 3}

# A high-resolution texture shown small: 32px stored, 8px tall on screen
tellraw @a {"render": "steel_ingot", "height": 8, "resolution": 32}

# Same item, height and resolution, but a different ascent: two glyphs, one texture
tellraw @a {"render": "steel_ingot", "height": 8, "resolution": 32, "ascent": 2}

