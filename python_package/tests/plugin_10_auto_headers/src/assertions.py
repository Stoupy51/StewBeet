
# Assertions for: stewbeet.plugins.auto.headers

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── every function must have a "#>" header ────────────────────────────────
    for func_path, func_obj in ctx.data.functions.items():
        content: str = func_obj.text
        assert f"#> {func_path}" in content, \
            f"Function '{func_path}' must have a '#> {func_path}' header line"

    # ── root function: must list helper/do_work as a callee ──────────────────
    root_content: str = ctx.data.functions[f"{ns}:root"].text
    # The header plugin adds @within for callers; the function body has the call
    assert f"{ns}:helper/do_work" in root_content, \
        "root function must reference helper/do_work"

    # ── helper/do_work: must be annotated as called from root ─────────────────
    do_work_content: str = ctx.data.functions[f"{ns}:helper/do_work"].text
    # @within shows the callers of this function
    assert "@within" in do_work_content, \
        "helper/do_work must have a @within annotation listing its callers"
    assert f"{ns}:root" in do_work_content, \
        "helper/do_work @within must list tns:root as a caller"

    # ── helper/log_result: called from do_work ────────────────────────────────
    log_result_content: str = ctx.data.functions[f"{ns}:helper/log_result"].text
    assert "@within" in log_result_content, \
        "helper/log_result must have a @within annotation"
    assert f"{ns}:helper/do_work" in log_result_content, \
        "helper/log_result @within must list helper/do_work as a caller"
