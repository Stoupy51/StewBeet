
# Imports
from beet import Context

from stewbeet import *  # type: ignore


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # Line numbers matter: assertions.py checks these exact call sites.
    write_function(f"{ns}:root", f"""
say Starting root
function {ns}:helper/do_work
""")

    write_function(f"{ns}:helper/do_work", """
say Doing work
scoreboard players add #count tns.data 1
""")

    # Beet function
    ctx.data[ns].functions["helper/do_work_2"] = Function("say Doing work 2")

    # A second contribution to the same function, from a different call site.
    write_function(f"{ns}:root", "say Appended later")
