
# Imports
from __future__ import annotations

import json
from typing import Any

from beet import Recipe
from stouputils.decorators import simple_cache
from stouputils.io import super_json_dump

from ...core.__memory__ import Mem
from ...core.ingredients import (
    get_item_from_ingredient,
    get_vanilla_item_id_from_ingredient,
    ingr_repr,
    ingr_to_id,
    item_to_id_ingr_repr,
    loot_table_from_ingredient,
)
from ...core.utils.io import write_function


class FurnaceRecipeHandler:
    """ Handler for furnace NBT recipe generation.

    This class handles the generation of custom furnace recipes with NBT data.
    """

    def __init__(self) -> None:
        """ Initialize the handler. """
        self.SMELTING: list[str] = ["smelting", "blasting", "smoking"]
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

    @simple_cache
    def furnace_nbt_recipe(self, recipe: dict[str, Any], result_loot: str, result_ingr: dict[str, Any]) -> str:
        """ Generate a furnace NBT recipe.

        Args:
            recipe (dict[str, Any]): The recipe data.
            result_loot (str): The loot table for the result.
            result_ingr (dict[str, Any]): The result ingredient.

        Returns:
            str: The generated recipe command.
        """
        ingredient: dict[str, Any] = recipe["ingredient"]
        result: dict[str, Any] = item_to_id_ingr_repr(get_item_from_ingredient(result_ingr))

        # Create a vanilla recipe for the furnace
        type: str = recipe["type"]
        ingredient_vanilla: str = get_vanilla_item_id_from_ingredient(ingredient)
        result_item: str = ingr_to_id(result_ingr).replace(':', '_')
        path: str = f"vanilla_items/{type}__{ingredient_vanilla.split(':')[1]}__{result_item}"
        type = f"minecraft:{type}" if ":" not in type else type
        json_file: dict[str, Any] = {
            "type": type,
            "ingredient": ingredient_vanilla,
            "result": result,
            "experience": recipe.get("experience", 0),
            "cookingtime": recipe.get("cookingtime", 200)
        }
        Mem.ctx.data["furnace_nbt_recipes"].recipes[path] = Recipe(super_json_dump(json_file, max_level=-1))

        # Prepare line and return
        line: str = "execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input"
        line += json.dumps(ingredient)
        line += f" run loot replace block ~ ~ ~ container.3 loot {result_loot}"
        return line

    @simple_cache()
    def furnace_xp_reward(self, recipe: dict[str, Any], experience: float) -> str:
        """ Generate a furnace XP reward.

        Args:
            recipe (dict[str, Any]): The recipe data.
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
        write_function(f"{self.FURNACE_NBT_PATH}/xp_reward/{experience}", file)

        # Create the recipe for the reward
        json_file: dict[str, Any] = {
            "type": "minecraft:smelting",
            "ingredient": "minecraft:command_block",
            "result": {"id": "minecraft:command_block"},
            "experience": experience,
            "cookingtime": 200
        }
        Mem.ctx.data["furnace_nbt_recipes"].recipes[f"xp/{experience}"] = Recipe(super_json_dump(json_file, max_level=-1))

        # Prepare line and return
        line: str = "execute if score #found furnace_nbt_recipes.data matches 0 store result score #found furnace_nbt_recipes.data if data storage furnace_nbt_recipes:main input"
        ingredient: dict[str, Any] = recipe["ingredient"]
        line += json.dumps(ingredient)
        line += f" run function {Mem.ctx.project_id}:calls/furnace_nbt_recipes/xp_reward/{experience}"
        return line

    def generate_recipes(self) -> None:
        """ Generate all furnace NBT recipes. """
        for item, data in Mem.database.items():
            crafts: list[dict[str, Any]] = list(data.get("result_of_crafting", []))
            crafts += list(data.get("used_for_crafting", []))

            for recipe in crafts:
                if recipe["type"] in self.SMELTING:
                    # Get ingredients
                    ingr = recipe.get("ingredients", {})
                    if not ingr:
                        ingr = recipe.get("ingredient", {})

                    # Get possible result item
                    if not recipe.get("result"):
                        result_loot_table = loot_table_from_ingredient(ingr_repr(item, Mem.ctx.project_id), recipe["result_count"])
                    else:
                        result_loot_table = loot_table_from_ingredient(recipe["result"], recipe["result_count"])

                    # Generate recipe
                    if recipe.get("result"):
                        line: str = self.furnace_nbt_recipe(recipe, result_loot_table, recipe["result"])
                    else:
                        line: str = self.furnace_nbt_recipe(recipe, result_loot_table, ingr_repr(item, Mem.ctx.project_id))

                    type: str = recipe["type"]
                    path: str = f"{self.FURNACE_NBT_PATH}/{type}_recipes"
                    write_function(path, line, tags=[f"furnace_nbt_recipes:v1/{type}_recipes"])

                    # Add vanilla item unless it's a custom item
                    if not ingr.get("item"):
                        self.furnace_nbt_vanilla_items.add(get_vanilla_item_id_from_ingredient(ingr))

                    # Add xp reward
                    experience: float = recipe.get("experience", 0)
                    if experience > 0:
                        line = self.furnace_xp_reward(recipe, experience)
                        path = f"{self.FURNACE_NBT_PATH}/recipes_used"
                        write_function(path, line, tags=["furnace_nbt_recipes:v1/recipes_used"])

