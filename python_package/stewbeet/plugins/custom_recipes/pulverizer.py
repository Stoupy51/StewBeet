
# Imports
import stouputils as stp

from ...core.__memory__ import Mem
from ...core.cls.external_item import ExternalItem
from ...core.cls.ingredients import Ingr
from ...core.cls.item import Item
from ...core.cls.recipe import PulverizingRecipe
from ...core.utils.io import write_function


class PulverizerRecipeHandler:
    """ Handler for pulverizer recipe generation.

    This class handles the generation of pulverizer recipes.
    """
    @classmethod
    def routine(cls) -> None:
        """ Main routine for pulverizer recipe generation. """
        handler = cls()
        handler.generate_recipes()

    @stp.simple_cache(method="str")
    def simplenergy_pulverizer_recipe(self, recipe: PulverizingRecipe, item: str) -> str:
        """ Generate a pulverizer recipe.

        Args:
            recipe (PulverizingRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            str: The generated recipe command.
        """
        if not recipe.ingredient:
            recipe.ingredient = Ingr(item)
        ingredient = recipe.ingredient.to_predicate()
        result = recipe.result.to_item().item_to_id() if recipe.result else Ingr(item)

        line: str = "execute if score #found simplenergy.data matches 0 store result score #found simplenergy.data if data storage simplenergy:main pulverizer.input"
        line += ExternalItem.json_dump(ingredient)
        line += f" run loot replace entity @s contents loot {result.register_loot_table(recipe.result_count)}"
        return line

    def generate_recipes(self) -> None:
        """ Generate all pulverizer recipes. """
        for item in Mem.definitions.keys():
            obj = Item.from_id(item)

            for recipe in obj.recipes:
                if recipe["type"] == PulverizingRecipe.type:
                    if not recipe.get("ingredient"):
                        recipe["ingredient"] = Ingr(item)
                    recipe = PulverizingRecipe.from_dict(recipe)
                    write_function(
                        f"{Mem.ctx.project_id}:calls/simplenergy/pulverizer_recipes",
                        self.simplenergy_pulverizer_recipe(recipe, item),
                        tags=["simplenergy:calls/pulverizer_recipes"],
                    )

