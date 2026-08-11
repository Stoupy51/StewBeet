
# Imports
import os

from beet import Context
from PIL import Image

from stewbeet import *  # type: ignore

# Item images the plugin must find instead of rendering or downloading them.
# Each one is a flat color so the assertions can tell them apart after resizing, and 64x64 so the
# difference between "stored untouched" and an explicit "resolution" is visible.
SEEDED_IMAGES: dict[str, tuple[int, int, int, int]] = {
    "tns/steel_ingot": (200, 200, 200, 255),
    "minecraft/stone": (120, 120, 120, 255),
    "mechanization/tin_ore": (180, 140, 90, 255),
}

# The oversized render, cut into a 2x2 grid of glyphs. Each quadrant is its own color so the
# assertions can tell which part of the source ended up in which tile.
QUADRANT_COLORS: list[tuple[int, int, int, int]] = [
    (255, 0, 0, 255),      # top left
    (0, 255, 0, 255),      # top right
    (0, 0, 255, 255),      # bottom left
    (255, 255, 0, 255),    # bottom right
]


# Main entry point
def beet_default(ctx: Context):
    # Seed the renders folder: these are the "source" images the plugin stores or shrinks
    for path, color in SEEDED_IMAGES.items():
        destination: str = f"iso_renders/{path}.png"
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        Image.new("RGBA", (64, 64), color).save(destination)

    # A 512x512 source, twice what Minecraft fits in one glyph: the plugin must cut it into tiles
    big: Image.Image = Image.new("RGBA", (512, 512))
    for index, quadrant in enumerate(QUADRANT_COLORS):
        big.paste(Image.new("RGBA", (256, 256), quadrant), (256 * (index % 2), 256 * (index // 2)))
    big.save("iso_renders/tns/big_logo.png")

    # Renders in an item lore: a project item, a vanilla one, and one from another pack
    Item(
        id="steel_ingot",
        base_item="minecraft:iron_ingot",
        manual_category="misc",
        components={
            "item_name": {"text": "Steel Ingot", "color": "white"},
            "lore": [[
                {"text": "Made of ", "color": "gray", "italic": False},
                {"render": "steel_ingot", "height": 8},
                {"render": "minecraft:stone"},
                {"render": "mechanization:tin_ore", "height": 12, "ascent": 3},
                # An explicit "resolution" shrinks the stored texture: 16px stored instead of the native 64px
                {"render": "steel_ingot", "height": 8, "resolution": 16},
                # Same item, height and resolution, but a different ascent: two glyphs, one texture
                {"render": "steel_ingot", "height": 8, "resolution": 16, "ascent": 2},
            ]],
        },
    )

    # An item whose render cannot be resolved: the node must survive untouched
    Item(
        id="ghost_ingot",
        base_item="minecraft:iron_ingot",
        manual_category="misc",
        components={
            "item_name": {"text": "Ghost Ingot", "color": "white"},
            "lore": [[{"render": "does_not_exist"}]],
        },
    )

    add_item_model_component()
    add_item_name_and_lore_if_missing()
