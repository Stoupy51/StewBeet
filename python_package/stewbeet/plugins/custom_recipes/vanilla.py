
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import cast

import stouputils as stp
from beet import Advancement, Recipe
from stouputils.typing import JsonDict

from ...core.__memory__ import Mem
from ...core.cls.ingredients import Ingr
from ...core.cls.item import Item
from ...core.cls.recipe import (
	BlastingRecipe,
	CampfireCookingRecipe,
	CraftingShapedRecipe,
	CraftingShapelessRecipe,
	RecipeBase,
	SmeltingRecipe,
	SmithingTransformRecipe,
	SmithingTrimRecipe,
	SmokingRecipe,
	StonecuttingRecipe,
	written_cooking_time,
)
from ...core.utils.io import set_json_encoder, write_function

# Constants
VANILLA_RECIPES: tuple[type[RecipeBase], ...] = (
	CraftingShapelessRecipe, CraftingShapedRecipe, SmeltingRecipe, BlastingRecipe, SmokingRecipe, CampfireCookingRecipe,
	StonecuttingRecipe, SmithingTransformRecipe, SmithingTrimRecipe,
)
""" The recipe types vanilla has a recipe file for. """

CookingRecipe = SmeltingRecipe | BlastingRecipe | SmokingRecipe | CampfireCookingRecipe


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

		if handler.vanilla_generated_recipes:
			handler.write_recipe_unlocking()

	def write_recipe_unlocking(self) -> None:
		""" A function giving every generated recipe, and an advancement unlocking each one when an ingredient or result is held. """
		ns: str = Mem.ctx.project_id
		recipes_given: str = "".join(f"recipe give @s {ns}:{recipe_file}\n" for recipe_file, _ in self.vanilla_generated_recipes)
		write_function(f"{ns}:utils/get_all_recipes", f"\n# Get all recipes\n{recipes_given}\n")

		# Every ingredient with the recipes it takes part in
		ingredients: dict[str, set[str]] = {}
		for recipe_name, _ in self.vanilla_generated_recipes:
			recipe: JsonDict = Mem.ctx.data[ns].recipes[recipe_name].data
			for ingr_str in Ingr.get_ingredients_from_vanilla_recipe(recipe):
				ingredients.setdefault(ingr_str, set()).add(recipe_name)

		adv_json: JsonDict = {
			"criteria": {"requirement": {"trigger": "minecraft:inventory_changed"}},
			"rewards": {"function": f"{ns}:advancements/unlock_recipes"}
		}
		Mem.ctx.data[f"{ns}:unlock_recipes"] = set_json_encoder(Advancement(adv_json), max_level=-1)

		content: str = f"""
# Revoke advancement
advancement revoke @s only {ns}:unlock_recipes

## For each ingredient in inventory, unlock the recipes
"""
		for ingr, recipes in ingredients.items():
			content += (
				f"# {ingr}\nscoreboard players set #success {ns}.data 0\n"
				f"execute store success score #success {ns}.data if items entity @s container.* {ingr}\n"
			)
			content += "".join(
				f"execute if score #success {ns}.data matches 1 run recipe give @s {ns}:{recipe_path}\n"
				for recipe_path in sorted(recipes)
			)
			content += "\n"

		content += "## Add result items\n"
		for recipe_name, item in self.vanilla_generated_recipes:
			content += (
				f"""execute if items entity @s container.* *[custom_data~{{"{ns}": {{"{item}":true}} }}] """
				f"run recipe give @s {ns}:{recipe_name}\n"
			)
		write_function(f"{ns}:advancements/unlock_recipes", content)

	def vanilla_shapeless_recipe(self, recipe: CraftingShapelessRecipe, item: str) -> JsonDict:
		"""Generate a vanilla shapeless recipe.

		Args:
			recipe: The recipe data.
			item:   The item to generate the recipe for.

		Returns:
			JsonDict: The generated recipe.
		"""
		result_ingr = recipe.result or Ingr(item)
		ingredients: list[str] = [i.to_vanilla_item_id() for i in recipe.ingredients]

		to_return: JsonDict = {
			"type": "minecraft:" + recipe.type,
			"category": recipe.category,
			"group": recipe.group,
			"ingredients": ingredients,
			"result": result_ingr.to_item().item_to_id(),
		}

		if not to_return["group"]:
			del to_return["group"]

		to_return["result"]["count"] = recipe["result_count"]
		return to_return

	def vanilla_shaped_recipe(self, recipe: CraftingShapedRecipe, item: str) -> JsonDict:
		"""Generate a vanilla shaped recipe.

		Args:
			recipe: The recipe data.
			item:   The item to generate the recipe for.

		Returns:
			JsonDict: The generated recipe.
		"""
		result_ingr = recipe.result or Ingr(item, Mem.ctx.project_id)
		ingredients: dict[str, str] = {
			k: i.to_vanilla_item_id()
			for k, i in recipe.ingredients.items()
		}

		to_return: JsonDict = {
			"type": "minecraft:" + recipe.type,
			"category": recipe.category,
			"group": recipe.group,
			"pattern": recipe.shape,
			"key": ingredients,
			"result": result_ingr.to_item().item_to_id(),
		}

		if not to_return["group"]:
			del to_return["group"]

		to_return["result"]["count"] = recipe.result_count
		return to_return

	@stp.simple_cache(method="str")
	def vanilla_furnace_recipe(
		self, recipe: SmeltingRecipe | BlastingRecipe | SmokingRecipe | CampfireCookingRecipe, item: str
	) -> JsonDict:
		""" Generate a vanilla furnace recipe.

		Args:
			recipe: The recipe data.
			item:   The item to generate the recipe for.

		Returns:
			JsonDict: The generated recipe.
		"""
		result_ingr = recipe.result or Ingr(item)
		ingredient_vanilla: str = recipe.ingredient.to_vanilla_item_id()

		to_return: JsonDict = {
			"type": "minecraft:" + recipe.type,
			"category": recipe.category,
			"group": recipe.group,
			"ingredient": ingredient_vanilla,
			"result": result_ingr.to_item().item_to_id(),
			"experience": recipe.experience,
			"cookingtime": written_cooking_time(recipe),
		}

		if not to_return["group"]:
			del to_return["group"]

		to_return["result"]["count"] = recipe.result_count
		return to_return

	@stp.simple_cache(method="str")
	def vanilla_stonecutting_recipe(self, recipe: StonecuttingRecipe, item: str) -> JsonDict:
		""" Generate a vanilla stonecutting recipe.

		Args:
			recipe: The recipe data.
			item:   The item to generate the recipe for.

		Returns:
			JsonDict: The generated recipe.
		"""
		result_ingr = recipe.result or Ingr(item, Mem.ctx.project_id)
		ingredient_vanilla: str = recipe.ingredient.to_vanilla_item_id()

		to_return: JsonDict = {
			"type": "minecraft:" + recipe.type,
			"group": recipe.group,
			"ingredient": ingredient_vanilla,
			"result": result_ingr.to_item().item_to_id(),
		}

		if not to_return["group"]:
			del to_return["group"]

		to_return["result"]["count"] = recipe.result_count
		return to_return

	@stp.simple_cache(method="str")
	def vanilla_smithing_transform_recipe(self, recipe: SmithingTransformRecipe, item: str) -> JsonDict:
		""" Generate a vanilla smithing transform recipe.

		Args:
			recipe: The recipe data.
			item:   The item to generate the recipe for.

		Returns:
			JsonDict: The generated recipe.
		"""
		result_ingr = recipe.result or Ingr(item)
		to_return: JsonDict = {
			"type": "minecraft:" + recipe.type,
			"base": recipe.base.to_vanilla_item_id(),
			"addition": recipe.addition.to_vanilla_item_id(),
			"template": recipe.template.to_vanilla_item_id(),
			"result": result_ingr.to_item().item_to_id(),
		}
		to_return["result"]["count"] = recipe.result_count
		return to_return

	@stp.simple_cache(method="str")
	def vanilla_smithing_trim_recipe(self, recipe: SmithingTrimRecipe, item: str) -> JsonDict:
		""" Generate a vanilla smithing trim recipe.

		Args:
			recipe: The recipe data.
			item:   The item to generate the recipe for.

		Returns:
			JsonDict: The generated recipe.
		"""
		return {
			"type": "minecraft:" + recipe.type,
			"base": recipe.base.to_vanilla_item_id(),
			"addition": recipe.addition.to_vanilla_item_id(),
			"template": recipe.template.to_vanilla_item_id(),
			"pattern": recipe.pattern,
		}

	def generate_recipes(self, override: list[str] | None = None) -> None:
		""" Generate all vanilla recipes.

		Args:
			override: If set, only generate recipes for this item, with override only.
				Used to regenerate a specific item.
		"""
		for item in Mem.definitions:
			if override and item not in override:
				continue
			i = 1
			for recipe in Item.from_id(item).recipes:
				content: JsonDict | None = self.vanilla_content(recipe, item)
				if content is None:
					continue
				name: str = f"{item}" if i == 1 else f"{item}_{i}"
				self.write_recipe_file(name, content)
				i += 1
				self.vanilla_generated_recipes.append((name, item))

	def vanilla_content(self, recipe: RecipeBase, item: str) -> JsonDict | None:
		""" The vanilla recipe file of a recipe, None when vanilla has no such type or an ingredient is not a plain item. """
		recipe_class: type[RecipeBase] | None = next((c for c in VANILLA_RECIPES if c.type == recipe["type"]), None)
		if recipe_class is None:
			return None
		typed: RecipeBase = recipe_class.from_dict(recipe)
		return self.vanilla_recipe(typed, item) if has_plain_ingredients(typed) else None

	def vanilla_recipe(self, recipe: RecipeBase, item: str) -> JsonDict:
		""" The vanilla recipe file of one of `VANILLA_RECIPES`. """
		if isinstance(recipe, CraftingShapelessRecipe):
			return self.vanilla_shapeless_recipe(recipe, item)
		if isinstance(recipe, CraftingShapedRecipe):
			return self.vanilla_shaped_recipe(recipe, item)
		if isinstance(recipe, StonecuttingRecipe):
			return self.vanilla_stonecutting_recipe(recipe, item)
		if isinstance(recipe, SmithingTransformRecipe):
			return self.vanilla_smithing_transform_recipe(recipe, item)
		if isinstance(recipe, SmithingTrimRecipe):
			return self.vanilla_smithing_trim_recipe(recipe, item)
		return self.vanilla_furnace_recipe(cast(CookingRecipe, recipe), item)

	def write_recipe_file(self, name: str, content: JsonDict) -> None:
		""" Write a recipe file.

		Args:
			name:    The name of the recipe.
			content: The recipe content.
		"""
		Mem.ctx.data[Mem.ctx.project_id].recipes[name] = set_json_encoder(Recipe(content), max_level=-1)


def has_plain_ingredients(recipe: RecipeBase) -> bool:
	""" Whether every ingredient of a recipe is a plain item, all a vanilla recipe file can name, and a trim has its pattern. """
	if isinstance(recipe, CraftingShapelessRecipe):
		return all(x.get("item") for x in recipe.ingredients)
	if isinstance(recipe, CraftingShapedRecipe):
		return all(x.get("item") for x in recipe.ingredients.values())
	if isinstance(recipe, SmithingTrimRecipe):
		return bool(recipe.base.get("item") and recipe.addition.get("item") and recipe.template.get("item") and recipe.pattern)
	if isinstance(recipe, SmithingTransformRecipe):
		return bool(recipe.base.get("item") and recipe.addition.get("item") and recipe.template.get("item"))
	return bool(cast(CookingRecipe | StonecuttingRecipe, recipe).ingredient.get("item"))

