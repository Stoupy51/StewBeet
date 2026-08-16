
# Assertions for: stewbeet.plugins.finalyze.unload

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version

    unload_path: str = f"{ns}:v{ver}/unload"

    # ── unload function must exist
    assert unload_path in ctx.data.functions, \
        f"versioned unload function must be generated: {unload_path}"
    unload_content: str = ctx.data.functions[unload_path].text

    # ── scoreboard objectives removal
    # The plugin scans for "scoreboard objectives add <name>" and generates removes
    assert f"scoreboard objectives remove {ns}.kills" in unload_content, \
        "unload must remove the tns.kills scoreboard objective"
    assert f"scoreboard objectives remove {ns}.deaths" in unload_content, \
        "unload must remove the tns.deaths scoreboard objective"

    # ── storage cleanup──────
    # The plugin scans for "data modify storage ns:key field" and generates removes
    assert f"data remove storage {ns}:state kills" in unload_content, \
        "unload must clear the tns:state kills storage field"
    assert f"data remove storage {ns}:state deaths" in unload_content, \
        "unload must clear the tns:state deaths storage field"

    # ── items clear─────────
    # Because item definitions exist, the unload must clear custom-data-tagged items
    assert f'clear @a *[custom_data~{{"{ns}":{{}}}}]' in unload_content, \
        "unload must clear custom items tagged with the namespace custom_data"

    # ── unload tag is registered
    unload_tag: str = f"{ns}:unload"
    assert unload_tag in ctx.data.function_tags or f"{ns}:v{ver}/unload" in ctx.data.functions, \
        "unload function or tag must be reachable from the pack's unload entry point"
