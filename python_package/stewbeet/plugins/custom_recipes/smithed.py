
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.external_item import ExternalItem
from ...core.cls.ingredients import Ingr
from ...core.cls.item import Item
from ...core.cls.recipe import CraftingShapedRecipe, CraftingShapelessRecipe
from ...core.utils.io import write_function
from ...dependencies.official_libs import OFFICIAL_LIBS, official_lib_used
from .. import sniffer


class SmithedRecipeHandler:
	""" Handler for Smithed Crafter recipe generation.

	This class handles the generation of custom recipes using Smithed Crafter.
	"""

	def __init__(self) -> None:
		""" Initialize the handler. """
		self.apply_path: str = f"{Mem.ctx.project_id}:calls/smithed_crafter/apply_recipe"

	@classmethod
	def routine(cls) -> None:
		"""Main routine for Smithed Crafter recipe generation."""
		handler = cls()
		handler.generate_recipes()

	@stp.simple_cache(method="str")
	def smithed_shapeless_recipe(self, recipe: CraftingShapelessRecipe, result_loot: str) -> str:
		""" Generate a Smithed Crafter shapeless recipe.

		Args:
			recipe:      The recipe data.
			result_loot: The loot table for the result.

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
			predicate = Ingr(ingr).to_predicate(count=count)
			r["recipe"].append(predicate)
		line += ExternalItem.json_dump(r)

		if recipe.smithed_crafter_command:
			line += f""" run function {self.apply_path} {{"command":"{recipe.smithed_crafter_command}"}}"""
		else:
			line += f""" run function {self.apply_path} {{"command":"loot replace block ~ ~ ~ container.16 loot {result_loot}"}}"""
		return line

	@stp.simple_cache(method="str")
	def smithed_shaped_recipe(self, recipe: CraftingShapedRecipe, result_loot: str) -> str:
		""" Generate a Smithed Crafter shaped recipe.

		Note: Shaped recipe predicates must NOT include 'count' because smithed.crafter's
		input storage omits count for individual slots. Shapeless predicates DO include
		count (the number of unique ingredient occurrences), which is handled separately.

		Args:
			recipe:      The recipe data.
			result_loot: The loot table for the result.

		Returns:
			str: The generated recipe command.
		"""
		# A layer is a row of the grid, empty when only air, else padded with air to its three slots
		layers: list[str] = []
		for layer in range(3):
			row: str = recipe.shape[layer] if layer < len(recipe.shape) else ""
			slots: list[JsonDict] = [self.slot_predicate(recipe.ingredients.get(char), slot) for slot, char in enumerate(row)]
			if all(slot.get("id") == "minecraft:air" for slot in slots):
				slots = []
			slots += [{"Slot": i, "id": "minecraft:air"} for i in range(len(slots), 3)] if slots else []
			layers.append(f"{layer}:[" + ",".join(self.slot_dump(slot) for slot in slots) + "]")

		command: str = recipe.smithed_crafter_command or f"loot replace block ~ ~ ~ container.16 loot {result_loot}"
		return (
			"execute if score @s smithed.data matches 0 "
			f"store result score @s smithed.data if data storage smithed.crafter:input recipe{{{','.join(layers)}}}"
			f""" run function {self.apply_path} {{"command":"{command}"}}"""
		)

	@staticmethod
	def slot_predicate(ingredient: Ingr | None, slot: int) -> JsonDict:
		""" What a slot of a shaped recipe must hold, air when no ingredient goes there.

		Without a count, since smithed.crafter's input storage omits it for individual slots.
		"""
		if not ingredient:
			return {"Slot": slot, "id": "minecraft:air"}
		predicate = ingredient.to_predicate(Slot=slot)
		predicate.pop("count", None)
		return predicate

	@staticmethod
	def slot_dump(predicate: JsonDict) -> str:
		""" A slot predicate as SNBT, its slot first and as a byte.

		>>> SmithedRecipeHandler.slot_dump({"id": "minecraft:air", "Slot": 2})
		'{"Slot":2b, "id": "minecraft:air"}'
		"""
		fields: JsonDict = predicate.copy()
		slot: int = fields.pop("Slot")
		return f'{{"Slot":{slot}b, {ExternalItem.json_dump(fields)[1:-1]}}}'

	def write_recipe(self, item: str, recipe: CraftingShapedRecipe | CraftingShapelessRecipe) -> None:
		""" Write one crafting recipe of an item for the Smithed Crafter, needed as soon as an ingredient is a custom item. """
		ingr: list[Ingr] = list(recipe.ingredients.values()) if isinstance(recipe, CraftingShapedRecipe) else recipe.ingredients
		result_loot_table = (recipe.result or Ingr(item)).register_loot_table(recipe.result_count)

		if any(i.get("components") for i in ingr) and not official_lib_used("smithed.crafter"):
			stp.debug("Found a crafting table recipe using custom item in ingredients, adding 'smithed.crafter' dependency")
			# Add to the give_all function the heavy workbench give command
			write_function(f"{Mem.ctx.project_id}:_give_all", "loot give @s loot smithed.crafter:blocks/table\n", prepend=True)

		if isinstance(recipe, CraftingShapelessRecipe):
			line = self.smithed_shapeless_recipe(recipe, result_loot_table)
			write_function(
				f"{Mem.ctx.project_id}:calls/smithed_crafter/shapeless_recipes", line,
				tags=["smithed.crafter:event/shapeless_recipes"],
			)
		else:
			line = self.smithed_shaped_recipe(recipe, result_loot_table)
			write_function(
				f"{Mem.ctx.project_id}:calls/smithed_crafter/shaped_recipes", line, tags=["smithed.crafter:event/recipes"],
			)

	def generate_recipes(self) -> None:
		""" Generate all Smithed Crafter recipes. """
		for item, _ in sniffer.attributed(Mem.definitions.items()):
			obj = Item.from_id(item)

			for recipe in obj.recipes:
				if recipe["type"] == CraftingShapedRecipe.type:
					self.write_recipe(item, CraftingShapedRecipe.from_dict(recipe))
				elif recipe["type"] == CraftingShapelessRecipe.type:
					self.write_recipe(item, CraftingShapelessRecipe.from_dict(recipe))

		# Apply recipe
		if OFFICIAL_LIBS["smithed.crafter"]["is_used"]:
			write_function(self.apply_path, """
# Set the consume_tools flag
data modify storage smithed.crafter:input flags set value ["consume_tools"]

# Perform the loot command
$return run $(command)
""")

