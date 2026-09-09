# A beet plugin with no StewBeet helper in sight.

# Imports
from beet import Context, Function


# Main entry point
def beet_default(ctx: Context) -> None:
    ctx.data.functions["tns:direct"] = Function("say written by beet itself\nsay second line\n")
    ctx.data.functions["tns:appended"] = Function("say first\n")
    ctx.data.functions["tns:appended"].append("say appended after assignment\n")

    # Assigned empty, so nothing this line records overwrites what was recorded for the path before.
    ctx.data.functions["tns:grown"] = Function()
    ctx.data.functions["tns:grown"].append("say grown one\nsay grown two\n")
