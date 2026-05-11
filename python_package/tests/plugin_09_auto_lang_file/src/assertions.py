
# Assertions for: stewbeet.plugins.auto.lang_file

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    # ── en_us language file must exist ────────────────────────────────────────
    assert "minecraft:en_us" in ctx.assets.languages, \
        "minecraft:en_us language file must be generated"

    lang_data: dict = ctx.assets.languages["minecraft:en_us"].data
    assert len(lang_data) > 0, \
        "en_us language file must contain at least one translation entry"

    # ── every value in en_us must be a non-empty string ──────────────────────
    for key, value in lang_data.items():
        assert isinstance(value, str) and value.strip(), \
            f"Lang entry '{key}' must be a non-empty string, got: {value!r}"

    # ── loot-table text components must produce translate entries ─────────────
    # "Gold Ring" from the explicit item_name → must appear as a value somewhere
    all_values: set[str] = set(lang_data.values())
    assert any("Gold Ring" in v for v in all_values), \
        "en_us must contain 'Gold Ring' as a translated value"

    # "Copper Wire" is auto-generated from id → must also appear
    assert any("Copper Wire" in v for v in all_values), \
        "en_us must contain 'Copper Wire' (auto-generated from id)"

    # "A shiny ring" from the lore component
    assert any("A shiny ring" in v for v in all_values), \
        "en_us must contain the lore text 'A shiny ring'"

    # ── translate keys must follow a stable pattern ───────────────────────────
    # At least one key should be namespace-qualified (contains "tns")
    assert any("tns" in k for k in lang_data.keys()), \
        "At least one lang key must be scoped to the project namespace 'tns'"
