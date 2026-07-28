
# Imports
import stouputils as stp
from beet import Recipe
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.external_item import ExternalItem
from ...core.cls.ingredients import Ingr
from ...core.cls.item import Item
from ...core.cls.recipe import BlastingRecipe, SmeltingRecipe, SmokingRecipe
from ...core.constants import CUSTOM_ITEM_VANILLA
from ...core.utils.io import set_json_encoder, write_function


class FurnaceRecipeHandler:
    """ Handler for furnace NBT recipe generation.

    This class handles the generation of custom furnace recipes with NBT data.
    """

    def __init__(self) -> None:
        """ Initialize the handler. """
        self.FURNACE_NBT_PATH: str = f"{Mem.ctx.project_id}:calls/furnace_nbt_recipes"
        self.furnace_nbt_vanilla_items: set[str] = set()

    @classmethod
    def routine(cls) -> None:
        """ Main routine for furnace recipe generation. """
        handler = cls()
        handler.generate_recipes()

        # If furnace nbt recipes is used
        if handler.furnace_nbt_vanilla_items:
            # Add vanilla items in disable cooking
            for item in sorted(handler.furnace_nbt_vanilla_items):
                write_function(
                    f"{handler.FURNACE_NBT_PATH}/disable_cooking",
                    (
                        "execute if score #reset furnace_nbt_recipes.data matches 0 "
                        "store success score #reset furnace_nbt_recipes.data "
                        "if data storage furnace_nbt_recipes:main "
                        f"input{{\"id\":\"{item}\"}}"
                    ),
                    tags=["furnace_nbt_recipes:v1/disable_cooking"]
                )

    @stp.simple_cache(method="str")
    def furnace_nbt_recipe(self, recipe: SmeltingRecipe | BlastingRecipe | SmokingRecipe, result_loot: str, result_ingr: JsonDict) -> str:
        """ Generate a furnace NBT recipe.

        Args:
            recipe (SmeltingRecipe | BlastingRecipe | SmokingRecipe): The recipe data.
            result_loot (str): The loot table for the result.
            result_ingr (JsonDict): The result ingredient.

        Returns:
            str: The generated recipe command.
        """
        result_ingr = Ingr(result_ingr)
        result = result_ingr.to_item().item_to_id()

        # Create a vanilla recipe for the furnace
        ingredient_vanilla: str = recipe.ingredient.to_vanilla_item_id()
        result_item: str = result_ingr.to_id().replace(':', '_')
        path: str = f"vanilla_items/{recipe.type}__{ingredient_vanilla.split(':')[1]}__{result_item}"
        type = f"minecraft:{recipe.type}"
        json_file: JsonDict = {
            "type": type,
            "ingredient": ingredient_vanilla,
            "result": result,
            "experience": recipe.experience,
            "cookingtime": recipe.cookingtime
        }
        Mem.ctx.data["furnace_nbt_recipes"].recipes[path] = set_json_encoder(Recipe(json_file), max_level=-1)

        # Prepare line and return
        line: str = "execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input"
        line += ExternalItem.json_dump(recipe.ingredient.to_predicate())
        line += f" run loot replace block ~ ~ ~ container.3 loot {result_loot}"
        return line

    @stp.simple_cache(method="str")
    def furnace_xp_reward(self, recipe: SmeltingRecipe | BlastingRecipe | SmokingRecipe, experience: float) -> str:
        """ Generate a furnace XP reward.

        Args:
            recipe (SmeltingRecipe | BlastingRecipe | SmokingRecipe): The recipe data.
            experience (float): The experience to reward.

        Returns:
            str: The generated XP reward command.
        """
        # Create the function for the reward
        file: str = f"""
# Add RecipesUsed nbt to the furnace
scoreboard players set #count furnace_nbt_recipes.data 0
execute store result score #count furnace_nbt_recipes.data run data get storage furnace_nbt_recipes:main furnace.RecipesUsed."furnace_nbt_recipes:xp/{experience}"
scoreboard players add #count furnace_nbt_recipes.data 1
execute store result block ~ ~ ~ RecipesUsed."furnace_nbt_recipes:xp/{experience}" int 1 run scoreboard players get #count furnace_nbt_recipes.data
scoreboard players reset #count furnace_nbt_recipes.data
"""
        write_function(f"{self.FURNACE_NBT_PATH}/xp_reward/{experience}", file, overwrite=True)

        # Create the recipe for the reward
        json_file: JsonDict = {
            "type": "minecraft:smelting",
            "ingredient": CUSTOM_ITEM_VANILLA,
            "result": {"id": CUSTOM_ITEM_VANILLA},
            "experience": experience,
            "cookingtime": 200
        }
        Mem.ctx.data["furnace_nbt_recipes"].recipes[f"xp/{experience}"] = Recipe(stp.json_dump(json_file, max_level=-1))

        # Prepare line and return
        line: str = "execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input"
        line += ExternalItem.json_dump(recipe.ingredient.to_predicate())
        line += f" run function {Mem.ctx.project_id}:calls/furnace_nbt_recipes/xp_reward/{experience}"
        return line

    def generate_recipes(self) -> None:
        """ Generate all furnace NBT recipes. """
        for item in Mem.definitions.keys():
            obj = Item.from_id(item)

            for recipe in obj.recipes:
                if recipe["type"] in (SmeltingRecipe.type, BlastingRecipe.type, SmokingRecipe.type):
                    recipe = SmeltingRecipe.from_dict(recipe) if recipe["type"] == SmeltingRecipe.type else \
                             BlastingRecipe.from_dict(recipe) if recipe["type"] == BlastingRecipe.type else \
                             SmokingRecipe.from_dict(recipe)

                    # Get possible result item
                    if not recipe.result:
                        result_loot_table = Ingr(item).register_loot_table(recipe.result_count)
                    else:
                        result_loot_table = recipe.result.register_loot_table(recipe.result_count)

                    # Generate recipe
                    if recipe.result:
                        line: str = self.furnace_nbt_recipe(recipe, result_loot_table, recipe.result)
                    else:
                        line: str = self.furnace_nbt_recipe(recipe, result_loot_table, Ingr(item))

                    type: str = recipe.type
                    path: str = f"{self.FURNACE_NBT_PATH}/{type}_recipes"
                    write_function(path, line, tags=[f"furnace_nbt_recipes:v1/{type}_recipes"])

                    # Add vanilla item unless it's a custom item
                    if not recipe.ingredient.get("item"):
                        self.furnace_nbt_vanilla_items.add(Ingr(recipe.ingredient).to_vanilla_item_id())

                    # Add xp reward
                    experience: float = recipe.get("experience", 0)
                    if experience > 0:
                        line = self.furnace_xp_reward(recipe, experience)
                        path = f"{self.FURNACE_NBT_PATH}/recipes_used"
                        write_function(path, line, tags=["furnace_nbt_recipes:v1/recipes_used"])

