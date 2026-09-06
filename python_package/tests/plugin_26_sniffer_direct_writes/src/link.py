# Every way a function reaches the pack, so the map can be checked against each.

# Imports
from beet import Context, Function

from stewbeet.core import write_function


# Main entry point
def beet_default(ctx: Context) -> None:
    # The StewBeet helper, which is what capture is built around.
    write_function("tns:written", "say written by the helper\n")

    # beet's own idiom, in the shapes a plugin actually writes.
    ctx.data.functions["tns:direct_assign"] = Function("say direct assign\nsay second line\n")
    ctx.data["tns"].functions["via_namespace"] = Function("say via namespace\n")
    ctx.data[Function]["tns:via_filetype"] = Function("say via filetype\n")
    ctx.data.functions["tns:from_list"] = Function(["say from list one", "say from list two"])

    # Assigned empty and then appended to. The append is patched, but the object was never
    # tagged with a path, so the patch has nothing to record it against.
    ctx.data.functions["tns:appended"] = Function()
    ctx.data.functions["tns:appended"].append("say appended after assignment")

    # A helper write followed by an append through the same path, which is tagged and recorded.
    write_function("tns:written_then_appended", "say first\n")
    write_function("tns:written_then_appended", "say second\n")

