
# Imports
from beet import Advancement, Recipe
from beet.core.utils import JsonDict
from stouputils.decorators import simple_cache

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from ...core.cls.recipe import (
    BlastingRecipe,
    CampfireCookingRecipe,
    CraftingShapedRecipe,
    CraftingShapelessRecipe,
    SmeltingRecipe,
    SmithingTransformRecipe,
    SmithingTrimRecipe,
    SmokingRecipe,
    StonecuttingRecipe,
)
from ...core.ingredients import (
    get_ingredients_from_recipe,
    get_item_from_ingredient,
    get_vanilla_item_id_from_ingredient,
    ingr_repr,
    item_to_id_ingr_repr,
)
from ...core.utils.io import set_json_encoder, write_function


class VanillaRecipeHandler:
    """ Handler for vanilla recipe generation.

    This class handles the generation of vanilla recipes (shapeless, shaped, furnace, ...).
    """

    def __init__(self) -> None:
        """ Initialize the handler. """
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
            adv_json: JsonDict = {
                "criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}},
                "rewards": {"function": f"{Mem.ctx.project_id}:advancements/unlock_recipes"}
            }
            Mem.ctx.data[adv_path] = set_json_encoder(Advancement(adv_json), max_level=-1)

            # Write the function that will unlock the recipes
            content = f"""
# Revoke advancement
advancement revoke @s only {Mem.ctx.project_id}:unlock_recipes

## For each ingredient in inventory, unlock the recipes
"""
            # Add ingredients
            for ingr, recipes in ingredients.items():
                recipes_list: list[str] = sorted(recipes)
                content += (
                    f"# {ingr}\nscoreboard players set #success {Mem.ctx.project_id}.data 0\n"
                    f"execute store success score #success {Mem.ctx.project_id}.data if items entity @s container.* {ingr}\n"
                )
                for recipe_path in recipes_list:
                    content += f"execute if score #success {Mem.ctx.project_id}.data matches 1 run recipe give @s {Mem.ctx.project_id}:{recipe_path}\n"
                content += "\n"

            # Add result items
            content += "## Add result items\n"
            for recipe_name, item in handler.vanilla_generated_recipes:
                content += f"""execute if items entity @s container.* *[custom_data~{{"{Mem.ctx.project_id}": {{"{item}":true}} }}] run recipe give @s {Mem.ctx.project_id}:{recipe_name}\n"""

            write_function(f"{Mem.ctx.project_id}:advancements/unlock_recipes", content)

    def vanilla_shapeless_recipe(self, recipe: CraftingShapelessRecipe, item: str) -> JsonDict:
        """Generate a vanilla shapeless recipe.

        Args:
            recipe (CraftingShapelessRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            JsonDict: The generated recipe.
        """
        result_ingr = recipe.result or ingr_repr(item, Mem.ctx.project_id)
        ingredients: list[str] = [get_vanilla_item_id_from_ingredient(i) for i in recipe.ingredients]

        to_return: JsonDict = {
            "type": "minecraft:" + recipe.type,
            "category": recipe.category,
            "group": recipe.group,
            "ingredients": ingredients,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe["result_count"]
        return to_return

    def vanilla_shaped_recipe(self, recipe: CraftingShapedRecipe, item: str) -> JsonDict:
        """Generate a vanilla shaped recipe.

        Args:
            recipe (CraftingShapedRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            JsonDict: The generated recipe.
        """
        result_ingr = recipe.result or ingr_repr(item, Mem.ctx.project_id)
        ingredients: dict[str, str] = {
            k: get_vanilla_item_id_from_ingredient(i)
            for k, i in recipe.ingredients.items()
        }

        to_return: JsonDict = {
            "type": "minecraft:" + recipe.type,
            "category": recipe.category,
            "group": recipe.group,
            "pattern": recipe.shape,
            "key": ingredients,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe.result_count
        return to_return

    @simple_cache
    def vanilla_furnace_recipe(self, recipe: SmeltingRecipe | BlastingRecipe | SmokingRecipe | CampfireCookingRecipe, item: str) -> JsonDict:
        """ Generate a vanilla furnace recipe.

        Args:
            recipe (SmeltingRecipe | BlastingRecipe | SmokingRecipe | CampfireCookingRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            JsonDict: The generated recipe.
        """
        result_ingr = recipe.result or ingr_repr(item, Mem.ctx.project_id)
        ingredient_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.ingredient)

        to_return: JsonDict = {
            "type": "minecraft:" + recipe.type,
            "category": recipe.category,
            "group": recipe.group,
            "ingredient": ingredient_vanilla,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe.result_count
        return to_return

    @simple_cache
    def vanilla_stonecutting_recipe(self, recipe: StonecuttingRecipe, item: str) -> JsonDict:
        """ Generate a vanilla stonecutting recipe.

        Args:
            recipe (StonecuttingRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            JsonDict: The generated recipe.
        """
        result_ingr = recipe.result or ingr_repr(item, Mem.ctx.project_id)
        ingredient_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.ingredient)

        to_return: JsonDict = {
            "type": "minecraft:" + recipe.type,
            "group": recipe.group,
            "ingredient": ingredient_vanilla,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        if not to_return["group"]:
            del to_return["group"]

        to_return["result"]["count"] = recipe.result_count
        return to_return

    @simple_cache
    def vanilla_smithing_transform_recipe(self, recipe: SmithingTransformRecipe, item: str) -> JsonDict:
        """ Generate a vanilla smithing transform recipe.

        Args:
            recipe (SmithingTransformRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            JsonDict: The generated recipe.
        """
        result_ingr = recipe.result or ingr_repr(item, Mem.ctx.project_id)
        base_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.base)
        addition_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.addition)
        template_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.template)

        to_return: JsonDict = {
            "type": "minecraft:" + recipe.type,
            "base": base_vanilla,
            "addition": addition_vanilla,
            "template": template_vanilla,
            "result": item_to_id_ingr_repr(get_item_from_ingredient(result_ingr)),
        }

        to_return["result"]["count"] = recipe.result_count
        return to_return

    @simple_cache
    def vanilla_smithing_trim_recipe(self, recipe: SmithingTrimRecipe, item: str) -> JsonDict:
        """ Generate a vanilla smithing trim recipe.

        Args:
            recipe (SmithingTrimRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            JsonDict: The generated recipe.
        """
        base_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.base)
        addition_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.addition)
        template_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.template)
        pattern_vanilla: str = get_vanilla_item_id_from_ingredient(recipe.pattern)

        to_return: JsonDict = {
            "type": "minecraft:" + recipe.type,
            "base": base_vanilla,
            "addition": addition_vanilla,
            "template": template_vanilla,
            "pattern": pattern_vanilla,
        }

        return to_return

    def generate_recipes(self, override: list[str] | None = None) -> None:
        """ Generate all vanilla recipes.

        Args:
            override (list[str]): If set, only generate recipes for this item and with override only. Used to regenerate a specific item.
        """
        for item in Mem.definitions.keys():
            if override and item not in override:
                continue
            obj = Item.from_id(item)

            i = 1
            for recipe in obj.recipes:
                name = f"{item}" if i == 1 else f"{item}_{i}"

                # Handle different recipe types
                if recipe["type"] == CraftingShapelessRecipe.type:
                    recipe = CraftingShapelessRecipe.from_dict(recipe)
                    if all(i.get("item") for i in recipe.ingredients):
                        self.write_recipe_file(name, self.vanilla_shapeless_recipe(recipe, item))
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] == CraftingShapedRecipe.type:
                    recipe = CraftingShapedRecipe.from_dict(recipe)
                    if all(i.get("item") for i in recipe.ingredients.values()):
                        self.write_recipe_file(name, self.vanilla_shaped_recipe(recipe, item))
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] in (SmeltingRecipe.type, BlastingRecipe.type, SmokingRecipe.type, CampfireCookingRecipe.type):
                    recipe = SmeltingRecipe.from_dict(recipe) if recipe["type"] == SmeltingRecipe.type else \
                             BlastingRecipe.from_dict(recipe) if recipe["type"] == BlastingRecipe.type else \
                             SmokingRecipe.from_dict(recipe) if recipe["type"] == SmokingRecipe.type else \
                             CampfireCookingRecipe.from_dict(recipe)
                    if recipe.ingredient.get("item"):
                        self.write_recipe_file(name, self.vanilla_furnace_recipe(recipe, item))
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] == StonecuttingRecipe.type:
                    recipe = StonecuttingRecipe.from_dict(recipe)
                    if recipe.ingredient.get("item"):
                        self.write_recipe_file(name, self.vanilla_stonecutting_recipe(recipe, item))
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] == SmithingTransformRecipe.type:
                    recipe = SmithingTransformRecipe.from_dict(recipe)
                    if (recipe.base.get("item") and recipe.addition.get("item") and recipe.template.get("item")):
                        self.write_recipe_file(name, self.vanilla_smithing_transform_recipe(recipe, item))
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

                elif recipe["type"] == SmithingTrimRecipe.type:
                    recipe = SmithingTrimRecipe.from_dict(recipe)
                    if (recipe.base.get("item") and recipe.addition.get("item") and recipe.template.get("item") and recipe.pattern.get("item")):
                        self.write_recipe_file(name, self.vanilla_smithing_trim_recipe(recipe, item))
                        i += 1
                        self.vanilla_generated_recipes.append((name, item))

    def write_recipe_file(self, name: str, content: JsonDict) -> None:
        """ Write a recipe file.

        Args:
            name (str): The name of the recipe.
            content (JsonDict): The recipe content.
        """
        Mem.ctx.data[Mem.ctx.project_id].recipes[name] = set_json_encoder(Recipe(content), max_level=-1)

