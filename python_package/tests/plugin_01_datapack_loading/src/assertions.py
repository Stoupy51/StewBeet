
# Assertions for: stewbeet.plugins.datapack.loading
# Every assert verifies a specific output of the loading plugin.

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    version: str = ctx.project_version
    major, minor, patch = version.split(".")

    # Enumerate function
    enum_path: str = f"{ns}:v{version}/load/enumerate"
    assert enum_path in ctx.data.functions, f"Missing function: {enum_path}"
    enum_content: str = ctx.data.functions[enum_path].text
    assert f"scoreboard players set #{ns}.major load.status {major}" in enum_content, \
        "enumerate must set the major scoreboard"
    assert f"scoreboard players set #{ns}.minor load.status {minor}" in enum_content, \
        "enumerate must set the minor scoreboard"
    assert f"scoreboard players set #{ns}.patch load.status {patch}" in enum_content, \
        "enumerate must set the patch scoreboard"

    # Resolve function
    resolve_path: str = f"{ns}:v{version}/load/resolve"
    assert resolve_path in ctx.data.functions, f"Missing function: {resolve_path}"
    assert f"function {ns}:v{version}/load/main" in ctx.data.functions[resolve_path].text, \
        "resolve must call the main load function"

    # Main function
    assert f"{ns}:v{version}/load/main" in ctx.data.functions, \
        "load/main function must be generated"

    # Confirm load function
    confirm_path: str = f"{ns}:v{version}/load/confirm_load"
    assert confirm_path in ctx.data.functions, f"Missing function: {confirm_path}"
    confirm_content: str = ctx.data.functions[confirm_path].text
    assert f"scoreboard players set #{ns}.loaded load.status 1" in confirm_content, \
        "confirm_load must set loaded score"
    assert "tellraw @a[tag=convention.debug]" in confirm_content, \
        "confirm_load must send a tellraw to debug-tagged players"
    assert f"function {ns}:v{version}/load/set_items_storage" in confirm_content, \
        "confirm_load must call set_items_storage"

    # Set items storage function
    storage_path: str = f"{ns}:v{version}/load/set_items_storage"
    assert storage_path in ctx.data.functions, f"Missing function: {storage_path}"
    storage_content: str = ctx.data.functions[storage_path].text
    assert f"data modify storage {ns}:items all" in storage_content, \
        "set_items_storage must initialise the items storage"
    assert "item_alpha" in storage_content, \
        "set_items_storage must contain item_alpha"
    assert "item_beta" in storage_content, \
        "set_items_storage must contain item_beta"

    # Function tags
    assert f"{ns}:enumerate" in ctx.data.function_tags, \
        f"Missing function tag: {ns}:enumerate"
    assert f"{ns}:resolve" in ctx.data.function_tags, \
        f"Missing function tag: {ns}:resolve"
    assert f"{ns}:v{version}/load/enumerate" in ctx.data.function_tags[f"{ns}:enumerate"].text, \
        "enumerate tag must reference the versioned enumerate function"
    assert f"{ns}:v{version}/load/resolve" in ctx.data.function_tags[f"{ns}:resolve"].text, \
        "resolve tag must reference the versioned resolve function"
