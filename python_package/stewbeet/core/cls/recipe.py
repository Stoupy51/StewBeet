
# pyright: reportUnnecessaryIsInstance=false
# Imports
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from typing import Any, Literal, Self

from beet.core.utils import JsonDict

from ._utils import StMapping


# Base Class
@dataclass(kw_only=True)
class RecipeBase(StMapping):
    """ Base class for all recipe types. """
    type: str = ""
    """ The type of the recipe, e.g. 'crafting_shaped', 'smelting', etc. """
    result_count: int = 1
    """ (Optional) The number of items produced by the recipe. Default is 1. """
    category: str | None = None
    """ (Optional) The category of the recipe for organizing in the crafting book. """
    group: str | None = None
    """ (Optional) The group of the recipe for recipe book grouping. """
    result: JsonDict | None = None
    """ (Optional) The result item of the recipe. If None, defaults to the item being defined. """

    # Others
    manual_priority: int | None = None
    """ (Optional) Manual priority for recipe button sorting in the ingame-manual. Used to remove buttons when too many are present. """
    smithed_crafter_command: str | None = None
    """ (Optional) Custom command to be used with Smithed Crafter recipes. If None, defaults to giving the loot table. """

    def __post_init__(self) -> None:
        from ..ingredients import ALL_RECIPES_TYPES
        if "minecraft:" in self.type:
            self.type = self.type.replace("minecraft:", "", 1)
        if self.type not in ALL_RECIPES_TYPES:
            raise ValueError(f"Invalid recipe type: {self.type}")

    def __getitem__(self, key: str) -> Any:
        """Get item from recipe data as if it were a dictionary."""
        data = asdict(self)
        # Filter out None values to match dict behavior
        return {k: v for k, v in data.items() if v is not None}[key]

    def __setitem__(self, key: str, value: Any) -> None:
        return setattr(self, key, value)

    def __iter__(self) -> Iterator[str]:
        """Iterate over recipe keys."""
        data = asdict(self)
        return iter(k for k, v in data.items() if v is not None)

    def __len__(self) -> int:
        """Return the number of non-None fields."""
        data = asdict(self)
        return sum(1 for v in data.values() if v is not None)

    @classmethod
    def from_dict(cls, data: JsonDict | "StMapping", item_id: str = "") -> Self:
        """ Create an object based on a dictionary. """
        if isinstance(data, cls):
            return data
        return cls(**data)

    @staticmethod
    def _validate_ingredient(ingredient: JsonDict, name: str = "Ingredient") -> None:
        """Validate a single ingredient dictionary."""
        if not isinstance(ingredient, dict):
            raise ValueError(f"{name} must be a dictionary")
        if not ingredient.get("item") and not ingredient.get("components"):
            raise ValueError(f"{name} must have an 'item' or 'components' key")
        if ingredient.get("components") and not isinstance(ingredient["components"], dict):
            raise ValueError(f"{name} must have a dict 'components' key")

    @staticmethod
    def _validate_ingredients_list(ingredients: list[JsonDict]) -> None:
        """Validate a list of ingredients."""
        if not isinstance(ingredients, list):
            raise ValueError("Ingredients must be a list")
        for ingredient in ingredients:
            RecipeBase._validate_ingredient(ingredient, "Each ingredient")

    @staticmethod
    def _validate_numeric_fields(experience: Any, cookingtime: Any) -> None:
        """Validate experience and cookingtime fields for furnace recipes."""
        if not isinstance(experience, (float, int)):
            raise ValueError("Experience must be a float or int")
        if not isinstance(cookingtime, int):
            raise ValueError("Cookingtime must be an int")


# Crafting Recipes
@dataclass
class CraftingShapedRecipe(RecipeBase):
    """ Recipe for shaped crafting. """
    shape: list[str]
    """ The shape pattern for the crafting recipe. """
    ingredients: dict[str, JsonDict]
    """ Dictionary mapping shape symbols to ingredient specifications. """

    type = "crafting_shaped"

    def __post_init__(self) -> None:
        self.type = "crafting_shaped"
        super().__post_init__()

        # Validate shape
        if not isinstance(self.shape, list) or not self.shape:
            raise ValueError("Shape must be a non-empty list")
        if len(self.shape) > 3 or len(self.shape[0]) > 3:
            raise ValueError("Shape must have a maximum of 3 rows and 3 columns")
        row_size = len(self.shape[0])
        if any(len(row) != row_size for row in self.shape):
            raise ValueError("All rows in shape must have the same number of columns")

        # Validate ingredients
        if not isinstance(self.ingredients, dict):
            raise ValueError("Ingredients must be a dictionary")
        for symbol, ingredient in self.ingredients.items():
            self._validate_ingredient(ingredient, f"Ingredient for symbol '{symbol}'")
            if not any(symbol in line for line in self.shape):
                raise ValueError(f"Symbol '{symbol}' must appear in the shape")



@dataclass
class CraftingShapelessRecipe(RecipeBase):
    """ Recipe for shapeless crafting. """
    ingredients: list[JsonDict]
    """ List of ingredient specifications for shapeless crafting. """

    type = "crafting_shapeless"

    def __post_init__(self) -> None:
        self.type = "crafting_shapeless"
        super().__post_init__()
        self._validate_ingredients_list(self.ingredients)


# Furnace Recipes
@dataclass
class SmeltingRecipe(RecipeBase):
    """Recipe for smelting in a furnace."""
    ingredient: JsonDict
    """ The ingredient to be smelted. """
    experience: float = 0.0
    """ Experience points awarded when the recipe is used. """
    cookingtime: int = 200
    """ Cooking time in ticks (200 ticks = 10 seconds by default). """

    type = "smelting"

    def __post_init__(self) -> None:
        self.type = "smelting"
        super().__post_init__()
        self._validate_ingredient(self.ingredient)
        self._validate_numeric_fields(self.experience, self.cookingtime)


@dataclass
class BlastingRecipe(RecipeBase):
    """Recipe for blasting in a blast furnace."""
    ingredient: JsonDict
    """ The ingredient to be blasted. """
    experience: float = 0.0
    """ Experience points awarded when the recipe is used. """
    cookingtime: int = 100
    """ Cooking time in ticks (100 ticks = 5 seconds by default). """

    type = "blasting"

    def __post_init__(self) -> None:
        self.type = "blasting"
        super().__post_init__()
        self._validate_ingredient(self.ingredient)
        self._validate_numeric_fields(self.experience, self.cookingtime)


@dataclass
class SmokingRecipe(RecipeBase):
    """Recipe for smoking in a smoker."""
    ingredient: JsonDict
    """ The ingredient to be smoked. """
    experience: float = 0.0
    """ Experience points awarded when the recipe is used. """
    cookingtime: int = 100
    """ Cooking time in ticks (100 ticks = 5 seconds by default). """

    type = "smoking"

    def __post_init__(self) -> None:
        self.type = "smoking"
        super().__post_init__()
        self._validate_ingredient(self.ingredient)
        self._validate_numeric_fields(self.experience, self.cookingtime)


@dataclass
class CampfireCookingRecipe(RecipeBase):
    """Recipe for cooking on a campfire."""
    ingredient: JsonDict
    """ The ingredient to be cooked. """
    experience: float
    """ Experience points awarded when the recipe is used. """
    cookingtime: int
    """ Cooking time in ticks (600 ticks = 30 seconds by default). """

    type = "campfire_cooking"

    def __post_init__(self) -> None:
        self.type = "campfire_cooking"
        super().__post_init__()
        self._validate_ingredient(self.ingredient)
        self._validate_numeric_fields(self.experience, self.cookingtime)


# Smithing Recipes
@dataclass
class SmithingTransformRecipe(RecipeBase):
    """Recipe for smithing table transformation."""
    template: JsonDict
    """ The template item (e.g., upgrade template). """
    base: JsonDict
    """ The base item to be transformed. """
    addition: JsonDict
    """ The addition item (e.g., material). """

    type = "smithing_transform"

    def __post_init__(self) -> None:
        self.type = "smithing_transform"
        super().__post_init__()
        for name, ingredient in [("template", self.template), ("base", self.base), ("addition", self.addition)]:
            self._validate_ingredient(ingredient, name.capitalize())


@dataclass
class SmithingTrimRecipe(RecipeBase):
    """Recipe for applying armor trims."""
    template: JsonDict
    """ The trim template. """
    base: JsonDict
    """ The armor piece. """
    addition: JsonDict
    """ The material for the trim. """
    pattern: JsonDict
    """ The trim pattern. """

    type = "smithing_trim"

    def __post_init__(self) -> None:
        self.type = "smithing_trim"
        super().__post_init__()
        for name, ingredient in [("template", self.template), ("base", self.base), ("addition", self.addition), ("pattern", self.pattern)]:
            self._validate_ingredient(ingredient, name.capitalize())


# Other Recipes
@dataclass
class StonecuttingRecipe(RecipeBase):
    """Recipe for stonecutting."""
    ingredient: JsonDict
    """ The ingredient to be cut. """

    type = "stonecutting"

    def __post_init__(self) -> None:
        self.type = "stonecutting"
        super().__post_init__()
        self._validate_ingredient(self.ingredient)


# Custom/Special Recipes
@dataclass
class PulverizingRecipe(RecipeBase):
    """Custom recipe for SimplEnergy pulverizing."""
    ingredient: JsonDict
    """ The ingredient to be pulverized. """

    type = "simplenergy_pulverizing"

    def __post_init__(self) -> None:
        self.type = "simplenergy_pulverizing"
        super().__post_init__()
        self._validate_ingredient(self.ingredient)


@dataclass
class AwakenedForgeRecipe(RecipeBase):
    """Custom recipe for Stardust awakened forge."""
    ingredients: list[JsonDict]
    """ List of ingredients for the awakened forge. """
    particle: str | None = None
    """ (Optional) Particle effect for the recipe. """

    type = "stardust_awakened_forge"

    def __post_init__(self) -> None:
        self.type = "stardust_awakened_forge"
        super().__post_init__()
        self._validate_ingredients_list(self.ingredients)


# Hardcoded Recipes (minimal implementation)
@dataclass
class HardcodedRecipe(RecipeBase):
    """Recipe for special/hardcoded crafting types."""
    type: Literal[ # type: ignore
        "crafting_decorated_pot", "crafting_special_armordye", "crafting_special_bannerduplicate",
        "crafting_special_bookcloning", "crafting_special_firework_rocket", "crafting_special_firework_star",
        "crafting_special_firework_star_fade", "crafting_special_mapcloning", "crafting_special_mapextending",
        "crafting_special_repairitem", "crafting_special_shielddecoration", "crafting_special_tippedarrow",
        "crafting_transmute",
    ]


# Type alias for all recipe types
Recipe = (
    CraftingShapedRecipe | CraftingShapelessRecipe |
    SmeltingRecipe | BlastingRecipe | SmokingRecipe | CampfireCookingRecipe |
    SmithingTransformRecipe | SmithingTrimRecipe |
    StonecuttingRecipe |
    PulverizingRecipe | AwakenedForgeRecipe |
    HardcodedRecipe
)

