
# Assertions for: stewbeet.plugins.custom_paintings

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── datapack: painting_variant JSON files ─────────────────────────────────
    assert f"{ns}:test_painting" in ctx.data[ns].painting_variants, \
        "test_painting must have a painting_variant in the datapack"
    assert f"{ns}:stewbeet_painting" in ctx.data[ns].painting_variants, \
        "stewbeet_painting must have a painting_variant in the datapack"

    # Explicit painting: author and title must be set
    test_text: str = ctx.data[ns].painting_variants["test_painting"].text
    assert "Test Author" in test_text, \
        "test_painting variant must contain the explicit author"
    assert "Test Title" in test_text, \
        "test_painting variant must contain the explicit title"
    assert "stewbeet_painting_2x2" in test_text, \
        "test_painting variant must reference the 2x2 texture"
    assert '"width": 2' in test_text or '"width":2' in test_text, \
        "test_painting variant must have width=2"
    assert '"height": 2' in test_text or '"height":2' in test_text, \
        "test_painting variant must have height=2"

    # Minimal painting: author must default to project_author
    minimal_text: str = ctx.data[ns].painting_variants["stewbeet_painting"].text
    assert "test" in minimal_text, \
        "stewbeet_painting variant must contain the project_author as default"

    # ── resource pack: painting textures ──────────────────────────────────────
    assert f"{ns}:painting/stewbeet_painting_2x2" in ctx.assets[ns].textures, \
        "2x2 painting texture must be added to the resource pack"
    assert f"{ns}:painting/stewbeet_painting" in ctx.assets[ns].textures, \
        "stewbeet_painting texture must be added to the resource pack"

    # ── datapack: placeable painting tag ─────────────────────────────────────
    placeable_tag: str = "minecraft:placeable"
    assert placeable_tag in ctx.data["minecraft"].painting_variant_tags, \
        "minecraft:placeable painting_variant_tag must be created"
    placeable_text: str = ctx.data["minecraft"].painting_variant_tags["placeable"].text
    assert f"{ns}:test_painting" in placeable_text, \
        "test_painting must be in the placeable tag"
    assert f"{ns}:stewbeet_painting" in placeable_text, \
        "stewbeet_painting must be in the placeable tag"
