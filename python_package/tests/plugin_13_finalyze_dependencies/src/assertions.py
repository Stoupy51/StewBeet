
# Assertions for: stewbeet.plugins.finalyze.dependencies

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── Lantern Load: minecraft:load tag ──────────────────────────────────────
    assert "minecraft:load" in ctx.data.function_tags, \
        "minecraft:load function tag must be set up by dependencies"
    mc_load_text: str = ctx.data.function_tags["minecraft:load"].text
    assert "#load:_private/load" in mc_load_text, \
        "minecraft:load must reference #load:_private/load"

    # ── Lantern Load: load:_private/init function ─────────────────────────────
    assert "load:_private/init" in ctx.data.functions, \
        "load:_private/init function must be created"
    init_content: str = ctx.data.functions["load:_private/init"].text
    assert "load.status" in init_content, \
        "load:_private/init must set up the load.status objective"

    # ── Lantern Load: load:_private/load tag ──────────────────────────────────
    assert "load:_private/load" in ctx.data.function_tags, \
        "load:_private/load tag must be created"
    private_load_text: str = ctx.data.function_tags["load:_private/load"].text
    assert "#load:_private/init" in private_load_text, \
        "load:_private/load must include the init tag"
    assert "#load:load" in private_load_text, \
        "load:_private/load must include the load phase"

    # ── Lantern Load: load:load tag references this pack ──────────────────────
    assert "load:load" in ctx.data.function_tags, \
        "load:load tag must be created"
    load_load_text: str = ctx.data.function_tags["load:load"].text
    assert f"#{ns}:load" in load_load_text, \
        f"load:load must reference #{ns}:load for this pack"

    # ── Pack-specific load tag ────────────────────────────────────────────────
    assert f"{ns}:load" in ctx.data.function_tags, \
        f"{ns}:load tag must be created"
    ns_load_text: str = ctx.data.function_tags[f"{ns}:load"].text
    assert f"#{ns}:enumerate" in ns_load_text, \
        f"{ns}:load must reference #{ns}:enumerate"
    assert f"#{ns}:resolve" in ns_load_text, \
        f"{ns}:load must reference #{ns}:resolve"

    # ── Lantern Load: load:_private/init tag ──────────────────────────────────
    assert "load:_private/init" in ctx.data.function_tags, \
        "load:_private/init tag must be created"
