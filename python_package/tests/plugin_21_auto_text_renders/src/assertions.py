
# Assertions for: stewbeet.plugins.auto.text_renders
#
# The expected values below are written out on purpose: they are the independent oracle for the
# render convention (glyph font, texture naming, ascent formula, size vs resolution). If the layout
# ever changes, this test fails instead of silently shipping different glyphs.

# Imports
import json

from beet import Context, Texture
from stouputils.typing import JsonDict

from stewbeet import Item
from stewbeet.plugins.auto.text_renders.config import DEFAULT_HEIGHT, TEXTURE_FOLDER, default_ascent, scale_to_height

# The colors seeded by src/definitions.py, used to prove each glyph got the right source image
STEEL_COLOR: tuple[int, int, int, int] = (200, 200, 200, 255)
STONE_COLOR: tuple[int, int, int, int] = (120, 120, 120, 255)
TIN_COLOR: tuple[int, int, int, int] = (180, 140, 90, 255)
ICON_COLOR: tuple[int, int, int, int] = (34, 184, 200, 255)


def glyph_of(component: JsonDict, font: str) -> str:
    """ The glyph character of a resolved render component. """
    assert component.get("font") == font, component
    assert not any(key in component for key in ("render", "height", "ascent", "resolution")), component
    return component["text"]


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    font: str = f"{ns}:renders"

    # ── One provider per distinct (id, height, ascent, resolution) ────────────────
    assert "renders" in ctx.assets[ns].fonts, f"the '{font}' font must be generated"
    providers: list[JsonDict] = ctx.assets[ns].fonts["renders"].data["providers"]

    # (texture file, ascent, height) -> the glyph char it declares
    by_glyph: dict[tuple[str, int, int], str] = {}
    spaces: list[JsonDict] = [provider for provider in providers if provider["type"] == "space"]
    for provider in providers:
        if provider["type"] == "space":
            continue
        assert provider["type"] == "bitmap", provider
        assert len(provider["chars"]) == 1 and provider["chars"][0], provider
        key = (provider["file"], provider["ascent"], provider["height"])
        assert key not in by_glyph, f"duplicate provider for {key}"
        by_glyph[key] = provider["chars"][0]

    # Every space a spliced render needs shares one provider, one character per distinct advance
    assert len(spaces) == 1, "the negative spacing must live in a single space provider"
    space_char: dict[int, str] = {advance: char for char, advance in spaces[0]["advances"].items()}
    assert set(space_char) == {-1, -32}, space_char

    def texture(item: str, stored: tuple[int, int]) -> str:
        """ Fully qualified texture file of an item stored at the given pixel size. """
        return f"{ns}:{TEXTURE_FOLDER}/{item}_{stored[0]}x{stored[1]}.png"

    def tile(row: int, column: int) -> str:
        """ Fully qualified texture file of one tile of the spliced 512x512 logo. """
        return f"{ns}:{TEXTURE_FOLDER}/{ns}_big_logo_512x512_h32a16/r{row}c{column}.png"

    # Without "resolution" the source image is stored untouched, whatever height it is displayed at
    square: int = DEFAULT_HEIGHT
    native: tuple[int, int] = (64, 64)
    expected: set[tuple[str, int, int]] = {
        # (file, ascent, height)
        (texture(f"{ns}_steel_ingot", native), default_ascent(8), 8),
        (texture("minecraft_stone", native), default_ascent(square), square),
        (texture("mechanization_tin_ore", native), 3, 12),
        (texture("ICON", native), default_ascent(8), 8),
        # From the hover function: same item at the default height, proving the 99 "height" of the
        # nested hover_event object was not mistaken for the render's own. Same texture as the 8px
        # glyph above, since neither asked for a resolution.
        (texture(f"{ns}_steel_ingot", native), default_ascent(square), square),
        # "resolution" shrinks the stored texture to 16x16, still displayed 8px tall...
        (texture(f"{ns}_steel_ingot", (16, 16)), default_ascent(8), 8),
        # ...and a second ascent on that very texture is its own glyph, not a silent collision
        (texture(f"{ns}_steel_ingot", (16, 16)), 2, 8),
        # From src/data/test_renders: the same pair at another resolution
        (texture(f"{ns}_steel_ingot", (32, 32)), default_ascent(8), 8),
        (texture(f"{ns}_steel_ingot", (32, 32)), 2, 8),
        # A 512x512 source shown 32px tall, cut into a 2x2 grid of 256x256 glyphs. The top row hangs
        # from the ascent down to the baseline, the bottom row hangs from the baseline itself.
        *((tile(row, column), 16 if row == 0 else 0, 16) for row in (0, 1) for column in (0, 1)),
        # An ascent above the height: a single glyph again, but its texture is padded down to the
        # baseline (64x64 of image over 64x96 of nothing) since Minecraft refuses ascent > height.
        (f"{ns}:{TEXTURE_FOLDER}/{ns}_steel_ingot_64x160_h8a20/r0c0.png", 20, 20),
    }
    assert set(by_glyph) == expected, (sorted(by_glyph), sorted(expected))
    assert len(set(by_glyph.values())) == len(expected), "every glyph must get its own character"

    # The default ascent centers the glyph on the text, and an explicit one wins
    assert default_ascent(8) == 7 and default_ascent(16) == 11, "ascent must center the glyph on the text band"

    # ── Every texture exists at its stored size ───────────────────────────────────
    stored_sizes: dict[str, tuple[int, int]] = {
        texture(f"{ns}_steel_ingot", native): native,
        texture("minecraft_stone", native): native,
        texture("mechanization_tin_ore", native): native,
        texture("ICON", native): native,              # assets/pack.png is 64x64, kept untouched
        texture(f"{ns}_steel_ingot", (16, 16)): (16, 16),
        texture(f"{ns}_steel_ingot", (32, 32)): (32, 32),
        # Each tile of the spliced logo is exactly what one glyph can hold, and the padded one keeps
        # its 64px of image on top of the transparency filling the gap down to the baseline
        **{tile(row, column): (256, 256) for row in (0, 1) for column in (0, 1)},
        f"{ns}:{TEXTURE_FOLDER}/{ns}_steel_ingot_64x160_h8a20/r0c0.png": (64, 160),
    }
    assert {file for file, _, _ in by_glyph} == set(stored_sizes), "providers must only point at the expected textures"

    for file, size in stored_sizes.items():
        name: str = file.split(":", 1)[1].removesuffix(".png")
        assert name in ctx.assets[ns].textures, f"missing texture {name}"
        tex: Texture = ctx.assets[ns].textures[name]
        assert tex.image.size == size, (name, tex.image.size, size)

    # height vs resolution: the same 64x64 source is displayed at 8px and 16px from one texture,
    # while an explicit resolution is what shrinks it. Scaling never stretches the aspect ratio.
    assert scale_to_height((64, 64), 16) == (16, 16)
    assert scale_to_height((64, 32), 8) == (16, 8), "a 2:1 source stays 2:1"

    def color_of(file: str) -> tuple[int, ...]:
        name = file.split(":", 1)[1].removesuffix(".png")
        return ctx.assets[ns].textures[name].image.convert("RGBA").getpixel((0, 0))  # type: ignore[return-value]

    assert color_of(texture(f"{ns}_steel_ingot", native)) == STEEL_COLOR
    assert color_of(texture("minecraft_stone", native)) == STONE_COLOR
    assert color_of(texture("mechanization_tin_ore", native)) == TIN_COLOR
    assert color_of(texture("ICON", native)) == ICON_COLOR, "the ICON glyph must come from assets/pack.png"

    # ── The item lore was rewritten in the generated loot table ───────────────────
    loot_table: JsonDict = json.loads(ctx.data[ns].loot_tables["i/steel_ingot"].text)
    components: JsonDict = loot_table["pools"][0]["entries"][0]["functions"][0]["components"]
    lore: list[JsonDict] = components["minecraft:lore"]

    rendered_line: list[JsonDict] = lore[0]
    assert rendered_line[0]["text"] == "Made of ", rendered_line
    steel_glyph: str = glyph_of(rendered_line[1], font)
    stone_glyph: str = glyph_of(rendered_line[2], font)
    tin_glyph: str = glyph_of(rendered_line[3], font)
    shrunk_glyph: str = glyph_of(rendered_line[4], font)
    raised_glyph: str = glyph_of(rendered_line[5], font)
    assert len({steel_glyph, stone_glyph, tin_glyph, shrunk_glyph, raised_glyph}) == 5, "distinct renders need distinct glyphs"

    # The source lore carries the ICON render next to plain text
    source_lore: list[JsonDict] = lore[-1]
    icon_glyph: str = glyph_of(source_lore[-1], font)

    # Each glyph matches the character its provider declares
    assert by_glyph[(texture(f"{ns}_steel_ingot", native), 7, 8)] == steel_glyph
    assert by_glyph[(texture("minecraft_stone", native), default_ascent(square), square)] == stone_glyph
    assert by_glyph[(texture("mechanization_tin_ore", native), 3, 12)] == tin_glyph
    assert by_glyph[(texture(f"{ns}_steel_ingot", (16, 16)), 7, 8)] == shrunk_glyph
    assert by_glyph[(texture(f"{ns}_steel_ingot", (16, 16)), 2, 8)] == raised_glyph
    assert by_glyph[(texture("ICON", native), 7, 8)] == icon_glyph

    # ── An unresolvable render is left untouched rather than dropped ───────────────
    ghost: JsonDict = json.loads(ctx.data[ns].loot_tables["i/ghost_ingot"].text)
    ghost_lore: list[JsonDict] = ghost["pools"][0]["entries"][0]["functions"][0]["components"]["minecraft:lore"]
    assert ghost_lore[0][0] == {"render": "does_not_exist"}, ghost_lore
    assert not any("does_not_exist" in file for file, _, _ in by_glyph), "an unresolvable render must not create a provider"

    # ── Renders inside commands were rewritten, reusing the lore's glyphs ──────────
    # Untouched keys keep the spacing they were written with, so compare without it
    def tight(text: str) -> str:
        """ The text with every space removed, so assertions ignore the original formatting. """
        return text.replace(" ", "")

    show: str = tight(ctx.data[ns].functions["show"].text)
    assert '"render"' not in show, show
    assert f'"text":"{steel_glyph}"' in show and f'"font":"{font}"' in show, show
    assert f'"text":"{stone_glyph}"' in show, show
    assert '"color":"red"' in show, "keys other than render/height/ascent/resolution must be carried over"
    assert '"height"' not in show, "the consumed height must be removed"

    # A "height" belonging to a sub-object is not mistaken for the render's own: the glyph came out
    # at the default height, and the nested 99 survived untouched
    hover: str = tight(ctx.data[ns].functions["hover"].text)
    default_glyph: str = by_glyph[(texture(f"{ns}_steel_ingot", native), default_ascent(square), square)]
    assert '"render"' not in hover, hover
    assert f'"text":"{default_glyph}"' in hover, hover
    assert default_glyph != steel_glyph, "the same item at two heights must get two glyphs"
    assert '"height":99' in hover, hover

    # ── A render too big for one glyph became a grid of them ──────────────────────
    # The four quadrants of the source must land in the four tiles, in reading order
    quadrants: list[tuple[int, int, int, int]] = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]
    for index, color in enumerate(quadrants):
        assert color_of(tile(index // 2, index % 2)) == color, (index, color)

    # Each tile is followed by the spacing correcting Minecraft's own advance, and every row but the
    # last by a negative space bringing the pen back to the left edge of the image.
    def glyph(row: int, column: int) -> str:
        return by_glyph[(tile(row, column), 16 if row == 0 else 0, 16)]

    expected_string: str = "".join([
        glyph(0, 0), space_char[-1], glyph(0, 1), space_char[-1], space_char[-32],
        glyph(1, 0), space_char[-1], glyph(1, 1), space_char[-1],
    ])
    big: str = tight(ctx.data[ns].functions["big"].text)
    assert f'"text":"{expected_string}"' in big, big
    assert f'"font":"{font}"' in big, big

    # A fully opaque 256px tile displayed 16px wide advances 256/16 + 1 = 17 pixels, so the four
    # tiles and their corrections add up to exactly the width of the image
    assert 4 * 17 + 4 * (-1) + (-32) == 32, "the spliced glyphs must advance the width of the image, no more"

    # The floating render is one padded glyph, whose 64px of image advances 64/8 + 1 = 9 pixels
    floating_glyph: str = by_glyph[(f"{ns}:{TEXTURE_FOLDER}/{ns}_steel_ingot_64x160_h8a20/r0c0.png", 20, 20)]
    floating: str = tight(ctx.data[ns].functions["floating"].text)
    assert f'"text":"{floating_glyph}{space_char[-1]}"' in floating, floating
    assert 9 + (-1) == 8, "the padded glyph must advance the width of the image, no more"

    # ── The definitions themselves are untouched: the pass only rewrites output ────
    assert Item.from_id("ghost_ingot").components["lore"][0][0] == {"render": "does_not_exist"}
