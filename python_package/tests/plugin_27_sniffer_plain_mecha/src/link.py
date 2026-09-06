# Functions written the way a plain beet plugin writes them, with no StewBeet helper in sight.

# Imports
from beet import Context, Function


# Main entry point
def beet_default(ctx: Context) -> None:
    ctx.data.functions["tns:assembled"] = Function("say assembled in memory\nsay second line\n")
    ctx.data["tns"].functions["via_namespace"] = Function("say via namespace\n")

