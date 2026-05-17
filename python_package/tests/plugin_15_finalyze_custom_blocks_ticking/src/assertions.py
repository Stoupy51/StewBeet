
# Assertions for: stewbeet.plugins.finalyze.custom_blocks_ticking

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version

    # ── place_secondary: tag + counter commands appended ──────────────────────
    place_secondary_path: str = f"{ns}:custom_blocks/ticking_block/place_secondary"
    assert place_secondary_path in ctx.data.functions, \
        "ticking_block/place_secondary must exist"
    place_secondary_content: str = ctx.data.functions[place_secondary_path].text

    # Tag "tick" must be added when placing the block
    assert f"tag @s add {ns}.tick" in place_secondary_content, \
        "place_secondary must add the tick tag"
    assert f"scoreboard players add #tick_entities {ns}.data 1" in place_secondary_content, \
        "place_secondary must increment the tick entity counter"

    # Tag "second" must be added too
    assert f"tag @s add {ns}.second" in place_secondary_content, \
        "place_secondary must add the second tag"
    assert f"scoreboard players add #second_entities {ns}.data 1" in place_secondary_content, \
        "place_secondary must increment the second entity counter"

    # ── destroy: counter decrements appended ─────────────────────────────────
    destroy_path: str = f"{ns}:custom_blocks/ticking_block/destroy"
    assert destroy_path in ctx.data.functions, \
        "ticking_block/destroy must exist"
    destroy_content: str = ctx.data.functions[destroy_path].text
    assert f"scoreboard players remove #tick_entities {ns}.data 1" in destroy_content, \
        "destroy must decrement the tick entity counter"
    assert f"scoreboard players remove #second_entities {ns}.data 1" in destroy_content, \
        "destroy must decrement the second entity counter"

    # ── versioned tick function: dispatch to custom block tick ────────────────
    tick_path: str = f"{ns}:v{ver}/tick"
    assert tick_path in ctx.data.functions, \
        "versioned tick function must exist"
    tick_content: str = ctx.data.functions[tick_path].text
    assert f"function {ns}:custom_blocks/tick" in tick_content, \
        "versioned tick must dispatch to custom_blocks/tick"

    # ── custom_blocks/tick: dispatch to ticking_block/tick ────────────────────
    cb_tick_path: str = f"{ns}:custom_blocks/tick"
    assert cb_tick_path in ctx.data.functions, \
        "custom_blocks/tick dispatch function must be generated"
    cb_tick_content: str = ctx.data.functions[cb_tick_path].text
    assert f"function {ns}:custom_blocks/ticking_block/tick" in cb_tick_content, \
        "custom_blocks/tick must dispatch to ticking_block/tick"

    # ── versioned second function: dispatch to custom block second ────────────
    second_path: str = f"{ns}:v{ver}/second"
    assert second_path in ctx.data.functions, \
        "versioned second function must exist"
    second_content: str = ctx.data.functions[second_path].text
    assert f"function {ns}:custom_blocks/second" in second_content, \
        "versioned second must dispatch to custom_blocks/second"
