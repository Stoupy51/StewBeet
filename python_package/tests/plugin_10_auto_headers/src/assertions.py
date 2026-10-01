
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

    # ── menu_from_dialog: reachable only from a dialog button ────────────────
    # Regression guard: dialogs used to be invisible to the header plugin, so a function called
    # only from a dialog action was annotated "@within ???" and looked like dead code.
    dialog_menu_content: str = ctx.data.functions[f"{ns}:menu_from_dialog"].text
    assert f"dialog {ns}:config" in dialog_menu_content, \
        f"menu_from_dialog @within must list 'dialog {ns}:config' as a caller, got:\n{dialog_menu_content}"
    assert "???" not in dialog_menu_content, \
        "menu_from_dialog must not be reported as an orphan now that dialogs are scanned"
    assert "as the player & at current position" in dialog_menu_content, \
        "a dialog button runs as the clicking player, so @executed must say so"

    # ── calls the analysis used to miss ──────────────────────────────────────
    def within(path: str) -> str:
        return ctx.data.functions[path].text.split("\n\n")[0]

    assert f"{ns}:perks/apply" in within(f"{ns}:perks/apply/juggernog"), \
        "a placeholder in a macro call path must reach every function it can match"
    assert f"string in {ns}:box" in within(f"{ns}:give/weapon"), \
        "a quoted function id given to a macro must be listed as a string reference"
    assert f"enchantment {ns}:left_click" in within(f"{ns}:on_attack"), \
        "an enchantment run_function effect must be listed as a caller"
    assert "(public)" in within(f"{ns}:config"), \
        "an uncalled function outside the versioned folder is public, not dead"
    assert "???" in within(f"{ns}:v{ctx.project_version}/dead"), \
        "an uncalled function inside the versioned folder is still reported as dead"
