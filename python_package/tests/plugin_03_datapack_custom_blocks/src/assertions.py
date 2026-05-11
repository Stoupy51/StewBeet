
# Assertions for: stewbeet.plugins.datapack.custom_blocks

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── facing predicates (N / E / S / W) ────────────────────────────────────
    for face in ["north", "east", "south", "west"]:
        pred_path: str = f"{ns}:facing/{face}"
        assert pred_path in ctx.data.predicates, \
            f"Missing facing predicate: {pred_path}"
        pred_text: str = ctx.data.predicates[pred_path].text
        assert face in pred_text, \
            f"Facing predicate for '{face}' must contain the face name"

    # ── light level predicates (1–15) ─────────────────────────────────────────
    for level in range(1, 16):
        light_path: str = f"{ns}:light/{level}"
        assert light_path in ctx.data.predicates, \
            f"Missing light predicate for level {level}"
        light_text: str = ctx.data.predicates[light_path].text
        assert str(level) in light_text, \
            f"Light predicate for level {level} must contain the level value"

    # ── get_rotation function ─────────────────────────────────────────────────
    get_rotation_path: str = f"{ns}:custom_blocks/get_rotation"
    assert get_rotation_path in ctx.data.functions, \
        "get_rotation function must be generated"
    get_rotation_content: str = ctx.data.functions[get_rotation_path].text
    assert f"scoreboard players set #rotation {ns}.data" in get_rotation_content, \
        "get_rotation must set the #rotation score"

    # ── check_light and compute_brightness helper functions ───────────────────
    assert f"{ns}:custom_blocks/check_light" in ctx.data.functions, \
        "check_light function must be generated"
    assert f"{ns}:custom_blocks/compute_brightness" in ctx.data.functions, \
        "compute_brightness function must be generated"

    # ── per-block functions — blocks with an 'id' ─────────────────────────────
    # All four blocks with an id generate place_main + place_secondary
    for block in ["block_no_facing", "block_visual_facing", "block_with_facing"]:
        assert f"{ns}:custom_blocks/{block}/place_main" in ctx.data.functions, \
            f"place_main missing for {block}"
        assert f"{ns}:custom_blocks/{block}/place_secondary" in ctx.data.functions, \
            f"place_secondary missing for {block}"

    # block_with_facing uses get_rotation inside place_main
    place_main_content: str = ctx.data.functions[f"{ns}:custom_blocks/block_with_facing/place_main"].text
    assert f"function {ns}:custom_blocks/get_rotation" in place_main_content, \
        "block_with_facing/place_main must call get_rotation"
    # and must set the facing blockstate
    assert "facing=" in place_main_content, \
        "block_with_facing/place_main must set a facing blockstate"

    # block_visual_facing must call get_rotation in place_main (for the display rotation)
    visual_main_content: str = ctx.data.functions[f"{ns}:custom_blocks/block_visual_facing/place_main"].text
    assert f"function {ns}:custom_blocks/get_rotation" in visual_main_content, \
        "block_visual_facing/place_main must call get_rotation"

    # ── per-block functions — BlockAlternative (contents / item_frame) ────────
    assert f"{ns}:custom_blocks/block_contents/place_main" in ctx.data.functions, \
        "block_contents/place_main must be generated"
    assert f"{ns}:custom_blocks/block_contents/place_secondary" in ctx.data.functions, \
        "block_contents/place_secondary must be generated"
    assert f"{ns}:custom_blocks/block_contents/get_facing" in ctx.data.functions, \
        "block_contents/get_facing must be generated"
    # get_facing reads the Facing NBT from the item frame
    get_facing_content: str = ctx.data.functions[f"{ns}:custom_blocks/block_contents/get_facing"].text
    assert "Facing" in get_facing_content, \
        "get_facing must read the Facing NBT"

    # ── smithed.custom_block on_place tag ─────────────────────────────────────
    # At least one block should be hooked into the smithed.custom_block event
    on_place_tag: str = "smithed.custom_block:event/on_place"
    assert on_place_tag in ctx.data.function_tags, \
        "smithed.custom_block:event/on_place tag must be generated"
