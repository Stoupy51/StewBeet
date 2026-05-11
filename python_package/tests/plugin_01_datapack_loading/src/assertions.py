
# Assertions for: stewbeet.plugins.datapack.loading
# Every assert verifies a specific output of the loading plugin.

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version
    major, minor, patch = ver.split(".")

    # ── enumerate function ────────────────────────────────────────────────────
    enum_path: str = f"{ns}:v{ver}/load/enumerate"
    assert enum_path in ctx.data.functions, f"Missing function: {enum_path}"
    enum_content: str = ctx.data.functions[enum_path].text
    assert f"scoreboard players set #{ns}.major load.status {major}" in enum_content, \
        "enumerate must set the major scoreboard"
    assert f"scoreboard players set #{ns}.minor load.status {minor}" in enum_content, \
        "enumerate must set the minor scoreboard"
    assert f"scoreboard players set #{ns}.patch load.status {patch}" in enum_content, \
        "enumerate must set the patch scoreboard"

    # ── resolve function ──────────────────────────────────────────────────────
    resolve_path: str = f"{ns}:v{ver}/load/resolve"
    assert resolve_path in ctx.data.functions, f"Missing function: {resolve_path}"
    assert f"function {ns}:v{ver}/load/main" in ctx.data.functions[resolve_path].text, \
        "resolve must call the main load function"

    # ── main function ─────────────────────────────────────────────────────────
    assert f"{ns}:v{ver}/load/main" in ctx.data.functions, \
        "load/main function must be generated"

    # ── confirm_load function ─────────────────────────────────────────────────
    confirm_path: str = f"{ns}:v{ver}/load/confirm_load"
    assert confirm_path in ctx.data.functions, f"Missing function: {confirm_path}"
    confirm_content: str = ctx.data.functions[confirm_path].text
    assert f"scoreboard players set #{ns}.loaded load.status 1" in confirm_content, \
        "confirm_load must set loaded score"
    assert "tellraw @a[tag=convention.debug]" in confirm_content, \
        "confirm_load must send a tellraw to debug-tagged players"
    assert f"function {ns}:v{ver}/load/set_items_storage" in confirm_content, \
        "confirm_load must call set_items_storage"

    # ── set_items_storage function ────────────────────────────────────────────
    storage_path: str = f"{ns}:v{ver}/load/set_items_storage"
    assert storage_path in ctx.data.functions, f"Missing function: {storage_path}"
    storage_content: str = ctx.data.functions[storage_path].text
    assert f"data modify storage {ns}:items all" in storage_content, \
        "set_items_storage must initialise the items storage"
    assert "item_alpha" in storage_content, \
        "set_items_storage must contain item_alpha"
    assert "item_beta" in storage_content, \
        "set_items_storage must contain item_beta"

    # ── function tags ─────────────────────────────────────────────────────────
    assert f"{ns}:enumerate" in ctx.data.function_tags, \
        f"Missing function tag: {ns}:enumerate"
    assert f"{ns}:resolve" in ctx.data.function_tags, \
        f"Missing function tag: {ns}:resolve"
    assert f"{ns}:v{ver}/load/enumerate" in ctx.data.function_tags[f"{ns}:enumerate"].text, \
        "enumerate tag must reference the versioned enumerate function"
    assert f"{ns}:v{ver}/load/resolve" in ctx.data.function_tags[f"{ns}:resolve"].text, \
        "resolve tag must reference the versioned resolve function"
