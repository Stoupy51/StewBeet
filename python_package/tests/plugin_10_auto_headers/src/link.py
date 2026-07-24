
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Root function that calls a helper
    write_function(f"{ns}:root", f"""
say Starting root
function {ns}:helper/do_work
say Root done
""")

    # Helper function called by root, which calls another helper
    write_function(f"{ns}:helper/do_work", f"""
say Doing work
function {ns}:helper/log_result
scoreboard players add #count {ns}.data 1
""")

    # Leaf function with no outgoing calls
    write_function(f"{ns}:helper/log_result", f"""
say Work complete
tellraw @a [{{"text":"count: "}},{{"score":{{"name":"#count","objective":"{ns}.data"}}}}]
""")

    # Reachable ONLY from a dialog button: no mcfunction, tag, or advancement calls it.
    # Without the dialog pass in FunctionAnalyzer this would be reported as "@within ???".
    write_function(f"{ns}:menu_from_dialog", "say Opened from a dialog button")

    ctx.data[ns].dialogs["config"] = Dialog({
        "type": "minecraft:multi_action",
        "title": {"text": "Test"},
        "actions": [
            {"label": {"text": "Open"}, "action": {"type": "run_command", "command": f"/function {ns}:menu_from_dialog"}},
        ],
    })
