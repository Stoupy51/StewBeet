
# Imports
import json
from typing import Any

from stouputils.decorators import simple_cache

from ...core.__memory__ import Mem
from ...core.constants import PULVERIZING
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

    @simple_cache()
    def simplenergy_pulverizer_recipe(self, recipe: dict[str, Any], item: str) -> str:
        """ Generate a pulverizer recipe.

        Args:
            recipe (dict[str, Any]): The recipe data.
            item (str): The item to generate the recipe for.

        Returns:
            str: The generated recipe command.
        """
        ingredient: dict[str, Any] = item_to_id_ingr_repr(recipe["ingredient"])
        result: dict[str, Any] = item_to_id_ingr_repr(get_item_from_ingredient(recipe["result"])) if recipe.get("result") else ingr_repr(item, Mem.ctx.project_id)

        line: str = "execute if score #found simplenergy.data matches 0 store result score #found simplenergy.data if data storage simplenergy:main pulverizer.input"
        line += json.dumps(ingredient)
        line += f" run loot replace entity @s contents loot {loot_table_from_ingredient(result, recipe['result_count'])}"
        return line

    def generate_recipes(self) -> None:
        """ Generate all pulverizer recipes. """
        for item, data in Mem.definitions.items():
            crafts: list[dict[str, Any]] = list(data.get("result_of_crafting", []))
            crafts += list(data.get("used_for_crafting", []))

            for recipe in crafts:
                if recipe["type"] == PULVERIZING:
                    write_function(
                        self.SIMPLENERGY_PULVERIZER_PATH,
                        self.simplenergy_pulverizer_recipe(recipe, item),
                        tags=["simplenergy:calls/pulverizer_recipes"],
                    )

