
# Imports
import json

from beet.core.utils import JsonDict
from stouputils.decorators import simple_cache

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from ...core.cls.recipe import PulverizingRecipe
from ...core.ingredients import (
    get_item_from_ingredient,
    ingr_repr,
    item_to_id_ingr_repr,
    loot_table_from_ingredient,
)
from ...core.utils.io import write_function


class PulverizerRecipeHandler:
    """ Handler for pulverizer recipe generation.

    This class handles the generation of pulverizer recipes.
    """
    def __init__(self) -> None:
        """ Initialize the handler. """
        self.SIMPLENERGY_PULVERIZER_PATH: str = f"{Mem.ctx.project_id}:calls/simplenergy/pulverizer_recipes"

    @classmethod
    def routine(cls) -> None:
        """ Main routine for pulverizer recipe generation. """
        handler = cls()
        handler.generate_recipes()

    @simple_cache
    def simplenergy_pulverizer_recipe(self, recipe: PulverizingRecipe, item: str) -> str:
        """ Generate a pulverizer recipe.

        Args:
            recipe (PulverizingRecipe): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            str: The generated recipe command.
        """
        if not recipe.ingredient:
            recipe.ingredient = ingr_repr(item, Mem.ctx.project_id)
        ingredient: JsonDict = item_to_id_ingr_repr(recipe.ingredient)
        result: JsonDict = item_to_id_ingr_repr(get_item_from_ingredient(recipe.result)) if recipe.result else ingr_repr(item, Mem.ctx.project_id)

        line: str = "execute if score #found simplenergy.data matches 0 store result score #found simplenergy.data if data storage simplenergy:main pulverizer.input"
        line += json.dumps(ingredient)
        line += f" run loot replace entity @s contents loot {loot_table_from_ingredient(result, recipe.result_count)}"
        return line

    def generate_recipes(self) -> None:
        """ Generate all pulverizer recipes. """
        for item in Mem.definitions.keys():
            obj = Item.from_id(item)

            for recipe in obj.recipes:
                if recipe["type"] == PulverizingRecipe.type:
                    recipe = PulverizingRecipe.from_dict(recipe)
                    write_function(
                        self.SIMPLENERGY_PULVERIZER_PATH,
                        self.simplenergy_pulverizer_recipe(recipe, item),
                        tags=["simplenergy:calls/pulverizer_recipes"],
                    )

