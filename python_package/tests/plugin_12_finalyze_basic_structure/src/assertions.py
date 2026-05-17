
# Assertions for: stewbeet.plugins.finalyze.basic_datapack_structure

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    ver: str = ctx.project_version

    tick_path: str = f"{ns}:v{ver}/tick"
    tick_2_path: str = f"{ns}:v{ver}/tick_2"
    second_path: str = f"{ns}:v{ver}/second"

    # ── versioned tick function has been created and contains timer logic ─────
    assert tick_path in ctx.data.functions, \
        f"versioned tick function must be generated: {tick_path}"
    tick_content: str = ctx.data.functions[tick_path].text

    # Tick increments the tick_2 and second counters
    assert f"scoreboard players add #tick_2 {ns}.data 1" in tick_content, \
        "tick function must increment the tick_2 counter"
    assert f"scoreboard players add #second {ns}.data 1" in tick_content, \
        "tick function must increment the second counter"

    # Tick calls tick_2 when threshold is reached (≥3)
    assert f"execute if score #tick_2 {ns}.data matches 3.." in tick_content, \
        "tick function must fire tick_2 when counter reaches 3"
    assert f"function {ns}:v{ver}/tick_2" in tick_content, \
        "tick function must call the versioned tick_2 function"

    # Tick calls second when threshold is reached (≥20)
    assert f"execute if score #second {ns}.data matches 20.." in tick_content, \
        "tick function must fire second when counter reaches 20"
    assert f"function {ns}:v{ver}/second" in tick_content, \
        "tick function must call the versioned second function"

    # ── tick_2 function has reset prepended ───────────────────────────────────
    assert tick_2_path in ctx.data.functions, \
        f"versioned tick_2 must still exist: {tick_2_path}"
    tick_2_content: str = ctx.data.functions[tick_2_path].text
    # Reset comes first (prepend=True)
    reset_line: str = f"scoreboard players set #tick_2 {ns}.data 1"
    assert reset_line in tick_2_content, \
        "tick_2 must have its reset command prepended"
    # Original user content still present
    assert f"say every 2 ticks ({ns})" in tick_2_content, \
        "tick_2 must retain the original user content"
    # Reset must come BEFORE the user content
    assert tick_2_content.index(reset_line) < tick_2_content.index(f"say every 2 ticks ({ns})"), \
        "tick_2 reset must appear before the original content"

    # ── second function has reset prepended ───────────────────────────────────
    assert second_path in ctx.data.functions, \
        f"versioned second must exist: {second_path}"
    second_content: str = ctx.data.functions[second_path].text
    second_reset: str = f"scoreboard players set #second {ns}.data 0"
    assert second_reset in second_content, \
        "second must have its reset command prepended"
    assert f"say every second ({ns})" in second_content, \
        "second must retain the original user content"
