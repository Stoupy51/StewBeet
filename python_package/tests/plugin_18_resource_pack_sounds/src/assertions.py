
# Assertions for: stewbeet.plugins.resource_pack.sounds

# Imports
import json

from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── sounds.json must be present in the resource pack ─────────────────────
    assert "minecraft:sounds" in ctx.assets.extra, \
        "sounds.json must be generated in the resource pack"

    sounds_raw: str = ctx.assets.extra["minecraft:sounds"].text
    sounds_data: dict = json.loads(sounds_raw)
    assert len(sounds_data) > 0, \
        "sounds.json must contain at least one sound event"

    # ── numbered variants are grouped ─────────────────────────────────────────
    # dirt_bullet_impact_01/02/03 → grouped under one key "dirt_bullet_impact"
    # The key is namespace-qualified: "tns:dirt_bullet_impact"
    impact_key: str = f"{ns}:dirt_bullet_impact"
    assert impact_key in sounds_data, \
        f"Numbered variants (dirt_bullet_impact_01/02/03) must be grouped under '{impact_key}'"
    impact_entry: dict = sounds_data[impact_key]
    assert "sounds" in impact_entry, \
        "Grouped sound event must have a 'sounds' list"
    # All three variants must be present
    impact_sounds: list = impact_entry["sounds"]
    assert len(impact_sounds) == 3, \
        f"All 3 dirt_bullet_impact variants must be listed; got {len(impact_sounds)}"
    # Every entry must reference an OGG file via 'name'
    for entry in impact_sounds:
        if isinstance(entry, dict):
            assert "name" in entry, \
                "Each sound variant entry must have a 'name' field"
        else:
            assert isinstance(entry, str), \
                "Each sound entry must be a dict or string"

    # ── individual (non-numbered) sounds appear as their own event ────────────
    fireselect_key: str = f"{ns}:fireselect"
    assert fireselect_key in sounds_data, \
        f"Individual sound 'fireselect' must produce its own event '{fireselect_key}'"
    fireselect_entry: dict = sounds_data[fireselect_key]
    assert "sounds" in fireselect_entry, \
        "Individual sound event must have a 'sounds' list"
    # Only one variant in the group
    assert len(fireselect_entry["sounds"]) == 1, \
        "fireselect must have exactly one sound variant"
