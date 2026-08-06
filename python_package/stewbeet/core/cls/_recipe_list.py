
# Imports
from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from typing import Any, Self, SupportsIndex, cast

import stouputils as stp
from beet import ItemTag, NamespaceProxy
from beet.contrib.vanilla import Vanilla
from stouputils.typing import JsonDict


@stp.simple_cache
def get_vanilla_item_tags() -> dict[str, ItemTag]:
    from ..__memory__ import Mem

    # Derive a stable, version-scoped key: same pattern as download_manager's URL keys
    cache = Mem.ctx.cache["stewbeet"]
    cache_key = f"vanilla_item_tags-{Mem.ctx.minecraft_version}"

    cached_path = cache.get_path(cache_key)
    if cached_path.exists():
        raw: JsonDict = stp.json_load(cached_path)
        return {k: ItemTag(v) for k, v in raw.items()}

    # Cache miss - pay the full cost once to generate the file
    tags: NamespaceProxy[ItemTag] = Vanilla(ctx=Mem.ctx).data.item_tags
    stp.json_dump({k: t.data for k, t in tags.items()}, file=cached_path)
    return dict(tags)

# Custom list class for recipes
class RecipeList(list[Any]):
    """ Custom list that normalizes recipes when they are added and expands item tags. """

    __slots__ = ("item_id",)

    item_id: str

    def __init__(self, item_id: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.item_id = item_id
        # Normalize existing items
        temp_list = list(self)
        self.clear()
        for recipe in temp_list:
            normalized = self._normalize_recipe(recipe)
            super().append(normalized)
        # Try to expand tags if context is available
        self._try_expand_tags()

    def _resolve_tag_recursively(self, tag_path: str, visited: set[str] | None = None) -> list[str]:
        """ Resolve item tags recursively to get all items.

        Args:
            tag_path: The tag path (e.g., "#minecraft:eggs")
            visited: Set of already visited tags to avoid infinite loops

        Returns:
            List of resolved item IDs
        """
        if visited is None:
            visited = set()

        # Avoid infinite loops
        if tag_path in visited:
            return []
        visited.add(tag_path)

        # Remove the # prefix if present
        clean_tag = tag_path[1:] if tag_path.startswith("#") else tag_path

        # Get the tag data from context
        from ..__memory__ import Mem
        if not Mem.ctx:
            return [tag_path]  # Can't resolve without context

        # Make sure vanilla data is loaded
        tag_data = Mem.ctx.data.item_tags.get(clean_tag)
        if not tag_data:
            tag_data = get_vanilla_item_tags().get(clean_tag)
        if not tag_data:
            return [tag_path]  # Tag not found, return as-is

        # Get values from tag
        values: list[JsonDict | str] = tag_data.data.get("values", [])
        resolved_items: list[str] = []

        for value in values:
            # Handle dict format {"id": "...", "required": false}
            if isinstance(value, dict):
                value = value.get("id", "")

            if not value:
                continue

            # If it's another tag, resolve it recursively
            if value.startswith("#"):
                resolved_items.extend(self._resolve_tag_recursively(value, visited))
            else:
                # It's a regular item
                resolved_items.append(value)

        return resolved_items

    def _get_recipe_ingredients(self, recipe: Any) -> list[tuple[str, Any, list[str]]]:
        """ Extract all ingredients from a recipe with their paths.

        Args:
            recipe: The recipe object to extract ingredients from

        Returns:
            List of tuples (path_description, ingredient, path_keys)
        """
        ingredients: list[tuple[str, Any, list[str]]] = []

        if not hasattr(recipe, '__dict__'):
            return ingredients

        # Check for ingredient field (furnace recipes)
        if hasattr(recipe, 'ingredient'):
            ingredients.append(("ingredient", recipe.ingredient, ["ingredient"]))

        # Check for ingredients field (shapeless, awakened forge)
        if hasattr(recipe, 'ingredients'):
            if isinstance(recipe["ingredients"], list):
                for i, ing in enumerate(recipe["ingredients"]):
                    ingredients.append((f"ingredients[{i}]", ing, ["ingredients", str(i)]))
            elif isinstance(recipe["ingredients"], dict):
                for key, ing in recipe["ingredients"].items():
                    ingredients.append((f"ingredients[{key}]", ing, ["ingredients", key]))

        # Check for smithing recipe fields
        for field in ['template', 'base', 'addition']:
            if hasattr(recipe, field):
                ing = getattr(recipe, field)
                ingredients.append((field, ing, [field]))

        return ingredients

    def _expand_recipe_tags(self, recipe: Any) -> list[Any]:
        """ Expand a recipe by resolving item tags into multiple recipes.

        Args:
            recipe: The recipe object to expand

        Returns:
            List of recipes (original if no tags, or expanded versions)
        """
        ingredients_with_tags: list[tuple[list[str], list[str]]] = []

        # Find all ingredients that use tags
        for _, ingredient, path_keys in self._get_recipe_ingredients(recipe):
            # Check if ingredient has an "item" field that starts with "#"
            item_value: str | None = None
            if hasattr(ingredient, "get"):
                item_value = ingredient.get("item", "")

            if isinstance(item_value, str) and item_value.startswith("#"):
                tag_path = item_value
                resolved_items = self._resolve_tag_recursively(tag_path)
                if resolved_items and resolved_items != [tag_path]:  # Only if resolved successfully
                    ingredients_with_tags.append((path_keys, resolved_items))

        # If no tags found, return original recipe
        if not ingredients_with_tags:
            return [recipe]

        # Start with the original recipe
        current_recipes: list[Any] = [recipe]

        # For each ingredient with tags, multiply the recipes
        for path_keys, resolved_items in ingredients_with_tags:
            new_recipes: list[Any] = []
            for current_recipe in current_recipes:
                for item_id in resolved_items:
                    # Deep copy the recipe
                    recipe_copy: Any = deepcopy(current_recipe)

                    # Navigate to the ingredient and replace the tag
                    target: Any = recipe_copy
                    for key in path_keys[:-1]:
                        if isinstance(target, dict):
                            target = cast(Any, target[key])
                        else:
                            target = getattr(target, key)

                    # Replace the tag with the actual item
                    final_key: str = path_keys[-1]
                    ingredient_copy: dict[str, Any]
                    if isinstance(target, dict):
                        ingredient_copy = dict(cast(JsonDict, target[final_key]))
                    elif isinstance(target, list):
                        ingredient_copy = dict(cast(JsonDict, target[int(final_key)]))
                    else:
                        ingredient_obj = getattr(target, final_key)
                        if hasattr(ingredient_obj, 'copy'):
                            ingredient_copy = ingredient_obj.copy()
                        else:
                            ingredient_copy = dict(ingredient_obj)

                    # Update the item field
                    ingredient_copy["item"] = item_id

                    # Import Ingr to recreate the ingredient
                    from .ingredients import Ingr
                    new_ingredient = Ingr(ingredient_copy)

                    # Set it back
                    if isinstance(target, dict):
                        target[final_key] = new_ingredient
                    elif isinstance(target, list):
                        target[int(final_key)] = new_ingredient
                    else:
                        setattr(target, final_key, new_ingredient)
                    new_recipes.append(recipe_copy)
            current_recipes = new_recipes

        return current_recipes if current_recipes else [recipe]

    def _try_expand_tags(self) -> None:
        """ Try to expand tags if a real build context is available (not the placeholder). """
        from ..__memory__ import Mem
        from ..placeholder_context import PLACEHOLDER_CTX
        if Mem.ctx is not PLACEHOLDER_CTX:
            self.expand_tags_now()

    def expand_tags_now(self) -> None:
        """ Force expansion of all recipe tags. """
        temp_list = list(self)
        self.clear()
        for recipe in temp_list:
            expanded = self._expand_recipe_tags(recipe)
            for exp_recipe in expanded:
                super().append(exp_recipe)

    def _normalize_recipe(self, recipe: Any) -> Any:
        """ Add default group to recipe if missing.

        Args:
            recipe: The recipe object to normalize

        Returns:
            The normalized recipe
        """
        if hasattr(recipe, "get") and not recipe.get("group"):
            recipe["group"] = self.item_id
        return recipe

    def append(self, item: Any) -> None:
        normalized = self._normalize_recipe(item)
        super().append(normalized)
        self._try_expand_tags()

    def insert(self, index: SupportsIndex, item: Any) -> None:
        normalized = self._normalize_recipe(item)
        expanded = self._expand_recipe_tags(normalized)
        for i, recipe in enumerate(expanded):
            super().insert(int(index) + i, recipe)

    def extend(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.append(item)

    def __setitem__(self, index: SupportsIndex | slice, item: Any) -> None:
        if isinstance(index, slice):
            if not hasattr(item, '__iter__'):
                raise TypeError("can only assign an iterable")
            # For slices, expand all items
            expanded_all: list[Any] = []
            for i in item:
                normalized = self._normalize_recipe(i)
                expanded_all.extend(self._expand_recipe_tags(normalized))
            return super().__setitem__(index, expanded_all)
        else:
            # For single index, replace with first expanded recipe
            normalized = self._normalize_recipe(item)
            expanded = self._expand_recipe_tags(normalized)
            if expanded:
                super().__setitem__(index, expanded[0])
                # Insert additional expanded recipes after this index
                for i, recipe in enumerate(expanded[1:], 1):
                    super().insert(int(index) + i, recipe)

    def __iadd__(self, other: Iterable[Any]) -> Self:
        self.extend(other)
        return self

