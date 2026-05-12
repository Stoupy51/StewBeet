
# Assertions for: stewbeet.plugins.resource_pack.sounds

# Imports
import json

from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── sounds.json must be present in the resource pack (under project namespace) ──
    assert "sounds.json" in ctx.assets[ns].extra, \
        "sounds.json must be generated in the resource pack"

    sounds_raw: str = ctx.assets[ns].extra["sounds.json"].text
    sounds_data: dict = json.loads(sounds_raw)
    assert len(sounds_data) > 0, \
        "sounds.json must contain at least one sound event"

    # ── numbered variants are grouped ─────────────────────────────────────────
    # dirt_bullet_impact_01/02/03 → grouped under one key "dirt_bullet_impact"
    # Keys in sounds.json are NOT namespace-prefixed (the ns prefix appears in the sound paths)
    assert "dirt_bullet_impact" in sounds_data, \
        "Numbered variants (dirt_bullet_impact_01/02/03) must be grouped under 'dirt_bullet_impact'"
    impact_entry: dict = sounds_data["dirt_bullet_impact"]
    assert "sounds" in impact_entry, \
        "Grouped sound event must have a 'sounds' list"
    # All three variants must be present
    impact_sounds: list = impact_entry["sounds"]
    assert len(impact_sounds) == 3, \
        f"All 3 dirt_bullet_impact variants must be listed; got {len(impact_sounds)}"
    # Every entry references a sound name including the namespace
    for entry in impact_sounds:
        assert isinstance(entry, str), \
            "Each sound entry must be a string name"
        assert ns in entry, \
            f"Each sound name must include the namespace '{ns}'"

    # ── individual (non-numbered) sounds appear as their own event ────────────
    assert "fireselect" in sounds_data, \
        "Individual sound 'fireselect' must produce its own event 'fireselect'"
    fireselect_entry: dict = sounds_data["fireselect"]
    assert "sounds" in fireselect_entry, \
        "Individual sound event must have a 'sounds' list"
    # Only one variant in the group
    assert len(fireselect_entry["sounds"]) == 1, \
        "fireselect must have exactly one sound variant"
