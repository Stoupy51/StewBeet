
# Assertions for: stewbeet.plugins.custom_recipes (furnace NBT handler)

# Imports
from stewbeet import Context, JsonDict


# Main entry point
def beet_default(ctx: Context):
    ns: str = ctx.project_id
    fnbt: str = f"{ns}:calls/furnace_nbt_recipes"

    # ── vanilla recipe files in furnace_nbt_recipes namespace ─────────────────
    # Smelting: raw_iron -> smelted_bar
    smelting_recipe: str = "vanilla_items/smelting__raw_iron__tns_smelted_bar"
    assert smelting_recipe in ctx.data["furnace_nbt_recipes"].recipes, \
        f"Expected smelting vanilla recipe: {smelting_recipe}"
    smelting_data: JsonDict = ctx.data["furnace_nbt_recipes"].recipes[smelting_recipe].data
    assert smelting_data.get("type") == "minecraft:smelting", \
        "smelting recipe must have type minecraft:smelting"
    assert smelting_data.get("cookingtime") == 200, \
        "smelting cookingtime must be 200"

    # Blasting: raw_iron -> smelted_bar
    blasting_recipe: str = "vanilla_items/blasting__raw_iron__tns_smelted_bar"
    assert blasting_recipe in ctx.data["furnace_nbt_recipes"].recipes, \
        f"Expected blasting vanilla recipe: {blasting_recipe}"
    blasting_data: JsonDict = ctx.data["furnace_nbt_recipes"].recipes[blasting_recipe].data
    assert blasting_data.get("type") == "minecraft:blasting", \
        "blasting recipe must have type minecraft:blasting"
    assert blasting_data.get("cookingtime") == 100, \
        "blasting cookingtime must be 100"

    # Smoking: beef -> smoked_food
    smoking_recipe: str = "vanilla_items/smoking__beef__tns_smoked_food"
    assert smoking_recipe in ctx.data["furnace_nbt_recipes"].recipes, \
        f"Expected smoking vanilla recipe: {smoking_recipe}"
    smoking_data: JsonDict = ctx.data["furnace_nbt_recipes"].recipes[smoking_recipe].data
    assert smoking_data.get("type") == "minecraft:smoking", \
        "smoking recipe must have type minecraft:smoking"

    # ── dispatch mcfunction files
    assert f"{fnbt}/smelting_recipes" in ctx.data.functions, \
        "calls/furnace_nbt_recipes/smelting_recipes function must be generated"
    assert f"{fnbt}/blasting_recipes" in ctx.data.functions, \
        "calls/furnace_nbt_recipes/blasting_recipes function must be generated"

    smelting_content: str = ctx.data.functions[f"{fnbt}/smelting_recipes"].text
    assert "furnace_nbt_recipes.data" in smelting_content, \
        "smelting_recipes must use the furnace_nbt_recipes.data scoreboard"
    assert "smelted_bar" in smelting_content, \
        "smelting_recipes must reference smelted_bar result"

    # ── function tags for furnace_nbt_recipes events ──────────────────────────
    assert "furnace_nbt_recipes:v1/smelting_recipes" in ctx.data.function_tags, \
        "furnace_nbt_recipes:v1/smelting_recipes tag must be created"
    assert "furnace_nbt_recipes:v1/blasting_recipes" in ctx.data.function_tags, \
        "furnace_nbt_recipes:v1/blasting_recipes tag must be created"

