
# Imports
from typing import Any

from beet import Advancement, Recipe
from beet.core.utils import JsonDict
from stouputils.decorators import simple_cache
from stouputils.io import super_json_dump

from ...core.__memory__ import Mem
from ...core.ingredients import get_ingredients_from_recipe, get_item_from_ingredient, get_vanilla_item_id_from_ingredient, ingr_repr, item_to_id_ingr_repr
from ...core.utils.io import write_function


class VanillaRecipeHandler:
    """ Handler for vanilla recipe generation.

    This class handles the generation of vanilla recipes (shapeless, shaped, furnace).
    """

    def __init__(self) -> None:
        """ Initialize the handler. """
        self.SMELTING: list[str] = ["smelting", "blasting", "smoking"]
        self.vanilla_generated_recipes: list[tuple[str, str]] = []

    @classmethod
    def routine(cls) -> None:
        """ Main routine for vanilla recipe generation. """
        handler = cls()
        handler.generate_recipes()

        # Create recipe unlocking function if vanilla recipes were generated
        if handler.vanilla_generated_recipes:
            # Create a function that will give all recipes
            content = "\n# Get all recipes\n"
            for recipe_file, _ in handler.vanilla_generated_recipes:
                content += f"recipe give @s {Mem.ctx.project_id}:{recipe_file}\n"
            write_function(f"{Mem.ctx.project_id}:utils/get_all_recipes", content + "\n")

            # Get all ingredients and their associated recipes
            ingredients: dict[str, set[str]] = {}
            for recipe_name, _ in handler.vanilla_generated_recipes:
                recipe: JsonDict = Mem.ctx.data[Mem.ctx.project_id].recipes[recipe_name].data
                for ingr_str in get_ingredients_from_recipe(recipe):
                    if ingr_str not in ingredients:
                        ingredients[ingr_str] = set()
                    ingredients[ingr_str].add(recipe_name)

            # Write the advancement
            adv_path: str = f"{Mem.ctx.project_id}:unlock_recipes"
            adv_json: dict[str, Any] = {
                "criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}},
                "rewards": {"function": f"{Mem.ctx.project_id}:advancements/unlock_recipes"}
            }
            Mem.ctx.data[adv_path] = Advancement(super_json_dump(adv_json, max_level=-1))

            # Write the function that will unlock the recipes
            content = f"""
# Revoke advancement
advancement revoke @s only {Mem.ctx.project_id}:unlock_recipes

## For each ingredient in inventory, unlock the recipes
"""
            # Add ingredients
            for ingr, recipes in ingredients.items():
                recipes: list[str] = sorted(recipes)
                content += (
                    f"# {ingr}\nscoreboard players set #success {Mem.ctx.project_id}.data 0\n"
                    f"execute store success score #success {Mem.ctx.project_id}.data if items entity @s container.* {ingr}\n"
                )
                for recipe in recipes:
                    content += f"execute if score #success {Mem.ctx.project_id}.data matches 1 run recipe give @s {Mem.ctx.project_id}:{recipe}\n"
                content += "\n"

            # Add result items
            content += "## Add result items\n"
            for recipe_name, item in handler.vanilla_generated_recipes:
                content += f"""execute if items entity @s container.* *[custom_data~{{"{Mem.ctx.project_id}": {{"{item}":true}} }}] run recipe give @s {Mem.ctx.project_id}:{recipe_name}\n"""

            write_function(f"{Mem.ctx.project_id}:advancements/unlock_recipes", content)

    @simple_cache()
    def vanilla_shapeless_recipe(self, recipe: dict[str, Any], item: str) -> dict[str, Any]:
        """Generate a vanilla shapeless recipe.

        Args:
            recipe (Dict[str, Any]): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            Dict[str, Any]: The generated recipe.
        """
        result_ingr = ingr_repr(item, Mem.ctx.project_id) if not recipe.get("result") else recipe["result"]
        ingredients: list[str] = [get_vanilla_item_id_from_ingredient(i) for i in recipe["ingredients"]]

        to_return = {
            "type": "minecraft:" + recipe["type"],
            "category": recipe["category"],
            "group": recipe.get("group"),
            "ingredients": ingredients,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe["result_count"]
        return to_return

    @simple_cache()
    def vanilla_shaped_recipe(self, recipe: dict[str, Any], item: str) -> dict[str, Any]:
        """Generate a vanilla shaped recipe.

        Args:
            recipe (Dict[str, Any]): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            Dict[str, Any]: The generated recipe.
        """
        result_ingr = ingr_repr(item, Mem.ctx.project_id) if not recipe.get("result") else recipe["result"]
        ingredients: dict[str, str] = {
            k: get_vanilla_item_id_from_ingredient(i)
            for k, i in recipe["ingredients"].items()
        }

        to_return = {
            "type": "minecraft:" + recipe["type"],
            "category": recipe["category"],
            "group": recipe.get("group"),
            "pattern": recipe["shape"],
            "key": ingredients,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe["result_count"]
        return to_return

    @simple_cache()
    def vanilla_furnace_recipe(self, recipe: dict[str, Any], item: str) -> dict[str, Any]:
        """ Generate a vanilla furnace recipe.

        Args:
            recipe (Dict[str, Any]): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            Dict[str, Any]: The generated recipe.
        """
        result_ingr = ingr_repr(item, Mem.ctx.project_id) if not recipe.get("result") else recipe["result"]
        ingredient_vanilla: str = get_vanilla_item_id_from_ingredient(recipe["ingredient"])

        to_return = {
            "type": "minecraft:" + recipe["type"],
            "category": recipe["category"],
            "group": recipe.get("group"),
            "ingredient": ingredient_vanilla,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe["result_count"]
        return to_return

    def generate_recipes(self) -> None:
        """ Generate all vanilla recipes. """
        for item, data in Mem.definitions.items():
            crafts: list[dict[str, Any]] = list(data.get("result_of_crafting", []))
            crafts += list(data.get("used_for_crafting", []))

            i = 1
            for recipe in crafts:
                name = f"{item}" if i == 1 else f"{item}_{i}"
                ingr = recipe.get("ingredients", {})
                if not ingr:
                    ingr = recipe.get("ingredient", {})

                # Handle different recipe types
                if recipe["type"] == "crafting_shapeless":
                    if all(isinstance(i, dict) and i.get("item") for i in ingr):
                        r = self.vanilla_shapeless_recipe(recipe, item)
                        self.write_recipe_file(name, r)
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] == "crafting_shaped":
                    if all(isinstance(i, dict) and i.get("item") for i in ingr.values()):
                        r = self.vanilla_shaped_recipe(recipe, item)
                        self.write_recipe_file(name, r)
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] in [*self.SMELTING, "campfire_cooking"]:
                    if isinstance(ingr, dict) and ingr.get("item"):
                        r = self.vanilla_furnace_recipe(recipe, item)
                        self.write_recipe_file(name, r)
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

    def write_recipe_file(self, name: str, content: dict[str, Any]) -> None:
        """ Write a recipe file.

        Args:
            name (str): The name of the recipe.
            content (dict[str, Any]): The recipe content.
        """
        r = Recipe(content)
        r.encoder = lambda x: super_json_dump(x, max_level=-1)
        Mem.ctx.data[Mem.ctx.project_id].recipes[name] = r

