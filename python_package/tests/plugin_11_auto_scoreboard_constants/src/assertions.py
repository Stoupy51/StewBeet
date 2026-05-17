
# Assertions for: stewbeet.plugins.auto.scoreboard_constants

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version

    # The plugin writes constants to the load/confirm_load file via write_load_file
    confirm_path: str = f"{ns}:v{ver}/load/confirm_load"
    assert confirm_path in ctx.data.functions, \
        f"confirm_load function must exist (required by scoreboard_constants): {confirm_path}"
    confirm_content: str = ctx.data.functions[confirm_path].text

    # All three constants used in the compute function must be initialised
    assert f"scoreboard players set #0 {ns}.data 0" in confirm_content, \
        "confirm_load must initialise constant #0"
    assert f"scoreboard players set #42 {ns}.data 42" in confirm_content, \
        "confirm_load must initialise constant #42"
    assert f"scoreboard players set #100 {ns}.data 100" in confirm_content, \
        "confirm_load must initialise constant #100"

    # Constants from the original loading functions (if any) must NOT be duplicated
    # (they are added only once each, the plugin uses a set)
    assert confirm_content.count("scoreboard players set #42") == 1, \
        "constant #42 must appear exactly once in confirm_load"
