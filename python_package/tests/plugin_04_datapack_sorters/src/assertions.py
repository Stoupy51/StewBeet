
# Assertions for: stewbeet.plugins.datapack.sorters

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    base: str = "tns:utils/sort_scores"

    # ── main sort entry function ──────────────────────────────────────────────
    assert f"{base}/sort" in ctx.data.functions, \
        "sort entry function must be generated"
    sort_content: str = ctx.data.functions[f"{base}/sort"].text
    assert "sorter:temp" in sort_content, \
        "sort function must use the sorter:temp storage"
    assert "selection_sort_loop" in sort_content, \
        "sort function must call selection_sort_loop"

    # ── selection_sort_loop function ──────────────────────────────────────────
    assert f"{base}/selection_sort_loop" in ctx.data.functions, \
        "selection_sort_loop function must be generated"
    loop_content: str = ctx.data.functions[f"{base}/selection_sort_loop"].text
    assert "find_min" in loop_content, \
        "selection_sort_loop must call find_min"
    assert "move_min_element" in loop_content, \
        "selection_sort_loop must call move_min_element"

    # ── find_min function ─────────────────────────────────────────────────────
    assert f"{base}/find_min" in ctx.data.functions, \
        "find_min function must be generated"
    find_min_content: str = ctx.data.functions[f"{base}/find_min"].text
    # The key ("score") and scale (100) must appear in the data get command
    assert "score" in find_min_content, \
        "find_min must use the configured key 'score'"
    assert "100" in find_min_content, \
        "find_min must use the configured scale 100"

    # ── move_min_element function (uses macros) ───────────────────────────────
    assert f"{base}/move_min_element" in ctx.data.functions, \
        "move_min_element function must be generated"
    move_content: str = ctx.data.functions[f"{base}/move_min_element"].text
    assert "$(min_index)" in move_content, \
        "move_min_element must use the $(min_index) macro"

    # ── append_remaining function (generated because limit is set) ────────────
    assert f"{base}/append_remaining" in ctx.data.functions, \
        "append_remaining function must be generated when a limit is configured"
