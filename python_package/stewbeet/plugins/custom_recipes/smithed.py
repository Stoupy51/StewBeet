
# Imports
import json

from beet.core.utils import JsonDict
from stouputils.decorators import simple_cache
from stouputils.print import debug

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from ...core.cls.recipe import CraftingShapedRecipe, CraftingShapelessRecipe
from ...core.constants import OFFICIAL_LIBS, official_lib_used
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
        self.SMITHED_APPLY_PATH: str = f"{Mem.ctx.project_id}:calls/smithed_crafter/apply_recipe"

    @classmethod
    def routine(cls) -> None:
        """Main routine for Smithed Crafter recipe generation."""
        handler = cls()
        handler.generate_recipes()

    @simple_cache
    def smithed_shapeless_recipe(self, recipe: CraftingShapelessRecipe, result_loot: str) -> str:
        """ Generate a Smithed Crafter shapeless recipe.

        Args:
            recipe (CraftingShapelessRecipe): The recipe data.
            result_loot (str): The loot table for the result.

        Returns:
            str: The generated recipe command.
        """
        # Get unique ingredients and their count
        unique_ingredients: list[tuple[int, JsonDict]] = []
        for ingr in recipe.ingredients:
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
        line: str = (
            "execute if score @s smithed.data matches 0 store result score @s smithed.data "
            f"if score count smithed.data matches {len(unique_ingredients)} if data storage smithed.crafter:input "
        )
        r: dict[str, list[JsonDict]] = {"recipe": []}
        for count, ingr in unique_ingredients:
            item: JsonDict = {"count": count}
            item.update(ingr)
            r["recipe"].append(item_to_id_ingr_repr(item))
        line += json.dumps(r)

        if recipe.smithed_crafter_command:
            line += f""" run function {self.SMITHED_APPLY_PATH} {{"command":"{recipe.smithed_crafter_command}"}}"""
        else:
            line += f""" run function {self.SMITHED_APPLY_PATH} {{"command":"loot replace block ~ ~ ~ container.16 loot {result_loot}"}}"""
        return line

    @simple_cache
    def smithed_shaped_recipe(self, recipe: CraftingShapedRecipe, result_loot: str) -> str:
        """ Generate a Smithed Crafter shaped recipe.

        Args:
            recipe (CraftingShapedRecipe): The recipe data.
            result_loot (str): The loot table for the result.

        Returns:
            str: The generated recipe command.
        """
        # Convert ingredients to aimed recipes
        ingredients: dict[str, JsonDict] = recipe.ingredients
        recipes: dict[int, list[JsonDict]] = {0: [], 1: [], 2: []}

        for i, row in enumerate(recipe.shape):
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
        if recipe.smithed_crafter_command:
            line += f""" run function {self.SMITHED_APPLY_PATH} {{"command":"{recipe.smithed_crafter_command}"}}"""
        else:
            line += f""" run function {self.SMITHED_APPLY_PATH} {{"command":"loot replace block ~ ~ ~ container.16 loot {result_loot}"}}"""
        return line

    def generate_recipes(self) -> None:
        """ Generate all Smithed Crafter recipes. """
        for item in Mem.definitions.keys():
            obj = Item.from_id(item)

            for recipe in obj.recipes:
                if recipe["type"] not in (CraftingShapelessRecipe.type, CraftingShapedRecipe.type):
                    continue
                recipe = CraftingShapedRecipe.from_dict(recipe) \
                    if recipe["type"] == CraftingShapedRecipe.type \
                    else CraftingShapelessRecipe.from_dict(recipe)

                # Get ingredients
                ingr: list[JsonDict] = list(recipe.ingredients.values()) if isinstance(recipe, CraftingShapedRecipe) else recipe.ingredients
                if not recipe.result:
                    result_loot_table = loot_table_from_ingredient(ingr_repr(item, Mem.ctx.project_id), recipe.result_count)
                else:
                    result_loot_table = loot_table_from_ingredient(recipe.result, recipe.result_count)

                # If there is a component in the ingredients of shaped/shapeless, use smithed crafter
                if any(i.get("components") for i in ingr):
                    if not official_lib_used("smithed.crafter"):
                        debug("Found a crafting table recipe using custom item in ingredients, adding 'smithed.crafter' dependency")

                        # Add to the give_all function the heavy workbench give command
                        write_function(f"{Mem.ctx.project_id}:_give_all", "loot give @s loot smithed.crafter:blocks/table\n", prepend=True)

                # Generate recipe based on type
                if isinstance(recipe, CraftingShapelessRecipe):
                    line = self.smithed_shapeless_recipe(recipe, result_loot_table)
                    write_function(self.SMITHED_SHAPELESS_PATH, line, tags=["smithed.crafter:event/shapeless_recipes"])
                else:
                    line = self.smithed_shaped_recipe(recipe, result_loot_table)
                    write_function(self.SMITHED_SHAPED_PATH, line, tags=["smithed.crafter:event/recipes"])

        # Apply recipe
        if OFFICIAL_LIBS["smithed.crafter"]["is_used"]:
            write_function(self.SMITHED_APPLY_PATH, """
# Set the consume_tools flag
data modify storage smithed.crafter:input flags set value ["consume_tools"]

# Perform the loot command
$return run $(command)
""")

