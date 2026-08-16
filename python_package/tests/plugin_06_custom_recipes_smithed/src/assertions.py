
# Assertions for: stewbeet.plugins.custom_recipes (Smithed Crafter handler)

# Imports
from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── shaped_recipes function
    shaped_path: str = f"{ns}:calls/smithed_crafter/shaped_recipes"
    assert shaped_path in ctx.data.functions, \
        "calls/smithed_crafter/shaped_recipes function must be generated"
    shaped_content: str = ctx.data.functions[shaped_path].text
    # The function must check smithed.data score and use smithed.crafter:input storage
    assert "smithed.data" in shaped_content, \
        "shaped_recipes must use the smithed.data scoreboard"
    assert "smithed.crafter:input" in shaped_content, \
        "shaped_recipes must read from smithed.crafter:input storage"
    # The recipe loot table is referenced to give the result
    assert "shaped_custom" in shaped_content, \
        "shaped_recipes must reference the shaped_custom item result"

    # ── shapeless_recipes function
    shapeless_path: str = f"{ns}:calls/smithed_crafter/shapeless_recipes"
    assert shapeless_path in ctx.data.functions, \
        "calls/smithed_crafter/shapeless_recipes function must be generated"
    shapeless_content: str = ctx.data.functions[shapeless_path].text
    assert "smithed.crafter:input" in shapeless_content, \
        "shapeless_recipes must read from smithed.crafter:input storage"
    assert "shapeless_custom" in shapeless_content, \
        "shapeless_recipes must reference the shapeless_custom result"

    # ── apply_recipe function
    apply_path: str = f"{ns}:calls/smithed_crafter/apply_recipe"
    assert apply_path in ctx.data.functions, \
        "calls/smithed_crafter/apply_recipe function must be generated"

    # ── function tags for smithed.crafter events ──────────────────────────────
    shaped_tag: str = "smithed.crafter:event/recipes"
    assert shaped_tag in ctx.data.function_tags, \
        "smithed.crafter:event/recipes tag must be created"
    assert ns in ctx.data.function_tags[shaped_tag].text, \
        "smithed.crafter:event/recipes tag must reference this namespace"

    shapeless_tag: str = "smithed.crafter:event/shapeless_recipes"
    assert shapeless_tag in ctx.data.function_tags, \
        "smithed.crafter:event/shapeless_recipes tag must be created"
    assert ns in ctx.data.function_tags[shapeless_tag].text, \
        "smithed.crafter:event/shapeless_recipes tag must reference this namespace"
