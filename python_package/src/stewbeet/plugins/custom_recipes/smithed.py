
# Imports
import json
from typing import Any

from stouputils.decorators import simple_cache

from ...core.__memory__ import Mem
from ...core.ingredients import (
    ingr_repr,
    item_to_id_ingr_repr,
    loot_table_from_ingredient,
)
from ...core.utils.io import write_function


class SmithedRecipeHandler:
    """ Handler for Smithed Crafter recipe generation.

    This class handles the generation of custom recipes using Smithed Crafter.
    """

    def __init__(self) -> None:
        """ Initialize the handler. """
        self.SMITHED_SHAPELESS_PATH: str = f"{Mem.ctx.project_id}:calls/smithed_crafter/shapeless_recipes"
        self.SMITHED_SHAPED_PATH: str = f"{Mem.ctx.project_id}:calls/smithed_crafter/shaped_recipes"

    @classmethod
    def routine(cls) -> None:
        """Main routine for Smithed Crafter recipe generation."""
        handler = cls()
        handler.generate_recipes()

    @simple_cache
    def smithed_shapeless_recipe(self, recipe: dict[str, Any], result_loot: str) -> str:
        """ Generate a Smithed Crafter shapeless recipe.

        Args:
            recipe (Dict[str, Any]): The recipe data.
            result_loot (str): The loot table for the result.

        Returns:
            str: The generated recipe command.
        """
        # Get unique ingredients and their count
        unique_ingredients: list[tuple[int, dict[str, Any]]] = []
        for ingr in recipe["ingredients"]:
            index: int = -1
            for i, (_, e) in enumerate(unique_ingredients):
                if str(ingr) == str(e):
                    index = i
                    break
            if index == -1:
                unique_ingredients.append((1, ingr))
            else:
                unique_ingredients[index] = (unique_ingredients[index][0] + 1, unique_ingredients[index][1])

        # Write the line
        line: str = f"execute if score @s smithed.data matches 0 store result score @s smithed.data if score count smithed.data matches {len(unique_ingredients)} if data storage smithed.crafter:input "
        r: dict[str, list[dict[str, Any]]] = {"recipe": []}
        for count, ingr in unique_ingredients:
            item: dict[str, Any] = {"count": count}
            item.update(ingr)
            r["recipe"].append(item_to_id_ingr_repr(item))
        line += json.dumps(r)

        if recipe.get("smithed_crafter_command"):
            line += f" run {recipe['smithed_crafter_command']}"
        else:
            line += f" run loot replace block ~ ~ ~ container.16 loot {result_loot}"
        return line + "\n"

    @simple_cache()
    def smithed_shaped_recipe(self, recipe: dict[str, Any], result_loot: str) -> str:
        """ Generate a Smithed Crafter shaped recipe.

        Args:
            recipe (Dict[str, Any]): The recipe data.
            result_loot (str): The loot table for the result.

        Returns:
            str: The generated recipe command.
        """
        # Convert ingredients to aimed recipes
        ingredients: dict[str, dict[str, Any]] = recipe["ingredients"]
        recipes: dict[int, list[dict[str, Any]]] = {0: [], 1: [], 2: []}

        for i, row in enumerate(recipe["shape"]):
            for slot, char in enumerate(row):
                ingredient = ingredients.get(char)
                if ingredient:
                    ingr = {"Slot": slot}
                    ingr.update(ingredient)
                    recipes[i].append(item_to_id_ingr_repr(ingr))
                else:
                    recipes[i].append({"Slot": slot, "id": "minecraft:air"})

        # Initialize the dump string
        dump: str = "{"

        # Iterate through each layer and its ingredients
        for i in range(3):
            if (i not in recipes) or (all(ingr.get("id") == "minecraft:air" for ingr in recipes[i])):
                recipes[i] = []

        for layer, ingrs in recipes.items():
            # If the list is empty, continue
            if not ingrs:
                dump += f"{layer}:[],"
                continue

            dump += f"{layer}:["  # Start of layer definition

            # Ensure each layer has exactly 3 ingredients by adding missing slots
            for i in range(len(ingrs), 3):
                ingrs.append({"Slot": i, "id": "minecraft:air"})

            # Process each ingredient in the layer
            for ingr in ingrs:
                ingr = ingr.copy()  # Create a copy to modify
                slot: int = ingr.pop("Slot")  # Extract the slot number
                ingr = json.dumps(ingr)[1:-1]  # Convert to JSON string without brackets
                dump += f'{{"Slot":{slot}b, {ingr}}},'  # Add the ingredient to the dump with its slot

            # Remove the trailing comma if present
            if dump[-1] == ',':
                dump = dump[:-1] + "],"  # End of layer definition
            else:
                dump += "],"  # End of layer definition without trailing comma

        # Remove the trailing comma if present and close the dump string
        if dump[-1] == ',':
            dump = dump[:-1] + "}"  # Close the dump string
        else:
            dump += "}"  # Close the dump string without trailing comma

        # Return the line
        line = f"execute if score @s smithed.data matches 0 store result score @s smithed.data if data storage smithed.crafter:input recipe{dump}"
        if recipe.get("smithed_crafter_command"):
            line += f" run {recipe['smithed_crafter_command']}"
        else:
            line += f" run loot replace block ~ ~ ~ container.16 loot {result_loot}"
        return line

    def generate_recipes(self) -> None:
        """Generate all Smithed Crafter recipes."""
        for item, data in Mem.database.items():
            crafts: list[dict[str, Any]] = list(data.get("result_of_crafting", []))
            crafts += list(data.get("used_for_crafting", []))

            for recipe in crafts:
                # Get ingredients
                ingr = recipe.get("ingredients", {})
                if not ingr:
                    ingr = recipe.get("ingredient", {})                # Get possible result item
                if not recipe.get("result"):
                    result_loot_table = loot_table_from_ingredient(ingr_repr(item, Mem.ctx.project_id), recipe["result_count"])
                else:
                    result_loot_table = loot_table_from_ingredient(recipe["result"], recipe["result_count"])

                # Generate recipe based on type
                if recipe["type"] == "crafting_shapeless":
                    line = self.smithed_shapeless_recipe(recipe, result_loot_table)
                    write_function(self.SMITHED_SHAPELESS_PATH, line, tags=["smithed.crafter:event/shapeless_recipes"])
                elif recipe["type"] == "crafting_shaped":
                    line = self.smithed_shaped_recipe(recipe, result_loot_table)
                    write_function(self.SMITHED_SHAPED_PATH, line, tags=["smithed.crafter:event/recipes"])

