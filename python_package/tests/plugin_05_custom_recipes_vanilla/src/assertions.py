
# Assertions for: stewbeet.plugins.custom_recipes (vanilla handler)

# Imports
import json

from beet import Context


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id

    # ── shaped recipe ─────────────────────────────────────────────────────────
    # The recipe file is stored under the namespace with the short key (no namespace prefix)
    assert "shaped_item" in ctx.data[ns].recipes, \
        "shaped_item must have a vanilla recipe file"
    shaped_data: dict = ctx.data[ns].recipes["shaped_item"].data
    assert shaped_data.get("type") == "minecraft:crafting_shaped", \
        "shaped_item recipe must be of type crafting_shaped"
    assert "pattern" in shaped_data, \
        "shaped recipe must contain a pattern"
    assert "key" in shaped_data, \
        "shaped recipe must contain ingredient keys"
    # 2×2 pattern: two rows of "XX"
    assert shaped_data["pattern"] == ["XX", "XX"], \
        "shaped_item pattern must be [['XX', 'XX']]"

    # ── shapeless recipe ──────────────────────────────────────────────────────
    assert "shapeless_item" in ctx.data[ns].recipes, \
        "shapeless_item must have a vanilla recipe file"
    shapeless_data: dict = ctx.data[ns].recipes["shapeless_item"].data
    assert shapeless_data.get("type") == "minecraft:crafting_shapeless", \
        "shapeless_item recipe must be of type crafting_shapeless"
    assert "ingredients" in shapeless_data, \
        "shapeless recipe must list ingredients"

    # ── stonecutting recipe ───────────────────────────────────────────────────
    assert "stone_slab" in ctx.data[ns].recipes, \
        "stone_slab must have a vanilla recipe file"
    stonecutting_data: dict = ctx.data[ns].recipes["stone_slab"].data
    assert stonecutting_data.get("type") == "minecraft:stonecutting", \
        "stone_slab recipe must be of type stonecutting"
    assert stonecutting_data["result"].get("count") == 2, \
        "stonecutting result_count must be 2"

    # ── smithing transform recipe ─────────────────────────────────────────────
    assert "smithed_item" in ctx.data[ns].recipes, \
        "smithed_item must have a vanilla recipe file"
    smithing_data: dict = ctx.data[ns].recipes["smithed_item"].data
    assert smithing_data.get("type") == "minecraft:smithing_transform", \
        "smithed_item recipe must be of type smithing_transform"
    assert "base" in smithing_data, \
        "smithing recipe must have a base ingredient"
    assert "addition" in smithing_data, \
        "smithing recipe must have an addition ingredient"

    # ── unlock_recipes advancement + function ─────────────────────────────────
    assert "unlock_recipes" in ctx.data[ns].advancements, \
        "unlock_recipes advancement must be generated"
    assert f"{ns}:utils/get_all_recipes" in ctx.data.functions, \
        "utils/get_all_recipes function must be generated"
    get_all_content: str = ctx.data.functions[f"{ns}:utils/get_all_recipes"].text
    assert "recipe give @s" in get_all_content, \
        "get_all_recipes must contain recipe give commands"
