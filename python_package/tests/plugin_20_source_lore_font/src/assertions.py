
# Assertions for: stewbeet.plugins.initialize.source_lore_font
#
# The expected values below are written out as literals ON PURPOSE: they are the independent
# oracle for the source lore convention (glyphs, font name, texture locations). If the font
# layout ever changes, this test fails instead of silently shipping a different lore.

# Imports
import colorsys

from beet import Context, Texture
from PIL import Image, ImageChops

from stewbeet import Item
from stewbeet.plugins.initialize.project_images import find_pack_png, find_tooltip_png
from stewbeet.plugins.initialize.source_lore_colors import (
    get_dominant_color,
    get_pixels,
    recolor_image,
    resolve_source_lore_color,
)
from stewbeet.plugins.initialize.source_lore_font import (
    ASSETS_FOLDER,
    ATLAS_TEXTURE,
    ICON_CHAR,
    ICON_TEXTURE,
    SPACER_CHAR,
    TOOLTIP_FONT,
    uses_font,
)

# The exact colors baked into tests/plugin_20_source_lore_font/assets/pack.png
LOGO_COLOR: tuple[int, int, int] = (34, 184, 200)  # Teal body, the only hue that survives filtering
GRAY_COLOR: tuple[int, int, int] = (128, 128, 128)  # Ignored: no saturation
FAINT_RED: tuple[int, int, int] = (220, 20, 20)     # Ignored: alpha below 128


def hue_of(color: tuple[int, int, int]) -> float:
    """ Hue of an RGB color, in degrees. """
    return colorsys.rgb_to_hsv(color[0] / 255, color[1] / 255, color[2] / 255)[0] * 360


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    font_id: str = f"{ns}:{TOOLTIP_FONT}"

    # ── The logo is discovered next to the project, not in the output directory ────
    logo_path = find_pack_png()
    assert logo_path is not None, "assets/pack.png must be discoverable from the project directory"
    assert logo_path.endswith("assets/pack.png"), logo_path
    assert find_tooltip_png() is None, "this project ships no tooltip.png override"
    assert ctx.meta["stewbeet"]["pack_icon_path"] == logo_path, ctx.meta["stewbeet"]["pack_icon_path"]

    # ── "auto" source lore: logo glyph + spacer + project name, all on the tooltip font ──
    source_lore = ctx.meta["stewbeet"]["source_lore"]
    assert source_lore[0] == "", "the lore must start with an empty string to reset the parent formatting"
    assert source_lore[1] == {"text": ICON_CHAR, "color": "white", "italic": False, "font": font_id}, source_lore[1]
    assert source_lore[2] == {"text": f"{SPACER_CHAR}{ctx.project_name}", "color": "white", "italic": False, "font": font_id}, source_lore[2]
    assert len(source_lore) == 3, source_lore
    assert uses_font(source_lore, font_id)
    assert not uses_font(source_lore, f"{ns}:something_else")

    # The lore was attached to the item, which is what makes last_final generate the font
    assert source_lore in Item.from_id("branded_item").components["lore"], "the source lore must be attached to the item"

    # ── The font was generated with the three providers of the packaged template ───
    assert TOOLTIP_FONT in ctx.assets[ns].fonts, f"last_final must generate the '{font_id}' font"
    providers = ctx.assets[ns].fonts[TOOLTIP_FONT].data["providers"]
    assert len(providers) == 3, providers

    # A space provider carrying the 2px spacer glyph
    assert providers[0]["type"] == "space", providers[0]
    assert providers[0]["advances"][SPACER_CHAR] == 2, providers[0]

    # The character atlas, retargeted from "ns:" to the project namespace
    assert providers[1]["type"] == "bitmap", providers[1]
    assert providers[1]["file"] == f"{ns}:{ATLAS_TEXTURE}.png", providers[1]
    assert "A" in "".join(providers[1]["chars"]), "the atlas must map the printable ASCII range"

    # The logo glyph
    assert providers[2]["file"] == f"{ns}:{ICON_TEXTURE}.png", providers[2]
    assert providers[2]["chars"] == [ICON_CHAR], providers[2]

    # ── Both textures exist, and the logo glyph is the untouched pack.png ──────────
    assert ATLAS_TEXTURE in ctx.assets[ns].textures, f"missing texture {ATLAS_TEXTURE}"
    assert ICON_TEXTURE in ctx.assets[ns].textures, f"missing texture {ICON_TEXTURE}"
    logo: Image.Image = Image.open(logo_path).convert("RGBA")
    icon_texture: Texture = ctx.assets[ns].textures[ICON_TEXTURE]
    assert ImageChops.difference(icon_texture.image.convert("RGBA"), logo).getbbox() is None, \
        "the logo glyph must be the pack.png (only images wider than 256px get resized)"

    # ── The dominant color ignores gray and mostly-transparent pixels ─────────────
    assert get_dominant_color(logo) == LOGO_COLOR, get_dominant_color(logo)
    assert get_dominant_color(Image.new("RGBA", (4, 4), (*GRAY_COLOR, 255))) is None
    assert get_dominant_color(Image.new("RGBA", (4, 4), (*FAINT_RED, 60))) is None

    # ── The atlas shipped with stewbeet was recolored towards the logo ─────────────
    packaged: Image.Image = Image.open(f"{ASSETS_FOLDER}/tooltip.png").convert("RGBA")
    atlas: Image.Image = ctx.assets[ns].textures[ATLAS_TEXTURE].image.convert("RGBA")
    assert atlas.size == packaged.size, (atlas.size, packaged.size)
    assert ImageChops.difference(atlas, recolor_image(packaged, LOGO_COLOR)).getbbox() is None, \
        "the generated atlas must be the packaged one recolored to the dominant logo color"

    # ── Every letter of the packaged atlas shares one baseline ─────────────────────
    # A bitmap provider has a single ascent, so uppercase and small-caps glyphs drawn at different
    # heights inside their 8x8 cell would render one pixel off from each other in the lore.
    letter_extents: set[tuple[int, int]] = set()
    for row, chars in enumerate(providers[1]["chars"]):
        for column, char in enumerate(chars):
            box = packaged.crop((column * 8, row * 8, column * 8 + 8, row * 8 + 8)).getbbox() if char.isalpha() else None
            if box is not None:
                letter_extents.add((box[1], box[3]))
    assert letter_extents == {(2, 7)}, f"every letter glyph must sit at y=2..7 in its cell, got {sorted(letter_extents)}"

    # The recolor moved the hue onto the logo, and did NOT flatten the gradient
    packaged_colors = {pixel[:3] for pixel in get_pixels(packaged) if pixel[3] > 0}
    atlas_colors = {pixel[:3] for pixel in get_pixels(atlas) if pixel[3] > 0}
    assert len(atlas_colors) == len(packaged_colors) > 1, (len(atlas_colors), len(packaged_colors))
    packaged_dominant = get_dominant_color(packaged)
    atlas_dominant = get_dominant_color(atlas)
    assert packaged_dominant is not None and atlas_dominant is not None
    # Not an exact match: the hue rotation lands the *average* pixel on the logo color, so the
    # heaviest bucket of the preserved gradient stays a few degrees off it (~11° for this atlas).
    assert abs(hue_of(atlas_dominant) - hue_of(LOGO_COLOR)) < 20, (atlas_dominant, LOGO_COLOR)
    assert abs(hue_of(packaged_dominant) - hue_of(LOGO_COLOR)) > 90, "the packaged atlas is gold, nowhere near the logo"

    # Transparent pixels keep their alpha, so the glyph shapes are untouched
    assert [pixel[3] for pixel in get_pixels(atlas)] == [pixel[3] for pixel in get_pixels(packaged)], \
        "the recolor must not touch the alpha channel"

    # ── source_lore_color accepts a color, a channel list, or disables the recolor ──
    stewbeet = ctx.meta["stewbeet"]
    try:
        assert resolve_source_lore_color(logo_path) == LOGO_COLOR, "the configured 'auto' must follow the logo"

        stewbeet["source_lore_color"] = "#55FFFF"
        assert resolve_source_lore_color(logo_path) == (85, 255, 255), resolve_source_lore_color(logo_path)

        stewbeet["source_lore_color"] = "gold"
        assert resolve_source_lore_color(logo_path) == (255, 215, 0), resolve_source_lore_color(logo_path)

        stewbeet["source_lore_color"] = [85, 255, 255]
        assert resolve_source_lore_color(logo_path) == (85, 255, 255), resolve_source_lore_color(logo_path)

        # Falsy values and "none"-ish strings mean "keep the packaged gold"
        for disabled in (False, "", "none", "false", "no", "off", "keep"):
            stewbeet["source_lore_color"] = disabled
            assert resolve_source_lore_color(logo_path) is None, f"{disabled!r} must disable the recolor"

        # An unparsable color warns and falls back to the logo instead of crashing the build
        stewbeet["source_lore_color"] = "not-a-color"
        assert resolve_source_lore_color(logo_path) == LOGO_COLOR, "an invalid color must fall back to 'auto'"

        # Without a logo there is nothing to derive the color from
        stewbeet["source_lore_color"] = "auto"
        assert resolve_source_lore_color(None) is None, "'auto' without a logo must not recolor"
    finally:
        stewbeet["source_lore_color"] = "auto"

    # ── recolor_image keeps a single-color image on the exact target ───────────────
    single: Image.Image = Image.new("RGBA", (2, 2), (255, 162, 20, 255))
    assert recolor_image(single, LOGO_COLOR).getpixel((0, 0)) == (*LOGO_COLOR, 255)
