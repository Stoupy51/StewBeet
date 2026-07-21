
# pyright: reportUnnecessaryIsInstance=false
# Imports
from dataclasses import dataclass
from typing import Any, Literal, Self

from stouputils.typing import JsonDict

from ._utils import StMapping
from .ingredients import ALL_RECIPES_TYPES, Ingr


# Base Class
# Beware: this hierarchy cannot use slots=True. Every subclass exposes its recipe type both as an
# instance field (`recipe.type`, serialized by to_dict()) and as a class-level constant compared
# against at ~15 call sites (`recipe["type"] == CraftingShapedRecipe.type`). dataclasses strips every
# field name from the class body when generating slots, so the constant would silently become a
# member descriptor and every one of those comparisons would evaluate to False without raising.
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
    result: Ingr | None = None
    """ (Optional) The result item of the recipe. If None, defaults to the item being defined. """

    # Others
    manual_priority: int | None = None
    """ (Optional) Manual priority for recipe button sorting in the ingame-manual. Used to remove buttons when too many are present. """
    smithed_crafter_command: str | None = None
    """ (Optional) Custom command to be used with Smithed Crafter recipes. If None, defaults to giving the loot table. """

    def __post_init__(self) -> None:
        if "minecraft:" in self.type:
            self.type = self.type.replace("minecraft:", "", 1)
        if self.type not in ALL_RECIPES_TYPES:
            raise ValueError(f"Invalid recipe type: {self.type}")

    @classmethod
    def from_dict(cls, data: JsonDict | StMapping, item_id: str = "") -> Self:
        """ Create an object based on a dictionary. """
        if isinstance(data, cls):
            return data
        return cls(**data)

    @staticmethod
    def validate_ingredient(ingredient: Ingr, name: str = "Ingredient") -> None:
        """ Validate a single ingredient dictionary. """
        if not isinstance(ingredient, dict):
            raise ValueError(f"{name} must be a dictionary")
        if not ingredient.get("item") and not ingredient.get("components"):
            raise ValueError(f"{name} must have an 'item' or 'components' key")
        if ingredient.get("components") and not isinstance(ingredient["components"], dict):
            raise ValueError(f"{name} must have a dict 'components' key")

    @staticmethod
    def validate_ingredients_list(ingredients: list[Ingr]) -> None:
        """ Validate a list of ingredients. """
        if not isinstance(ingredients, list):
            raise ValueError("Ingredients must be a list")
        for ingredient in ingredients:
            RecipeBase.validate_ingredient(ingredient, "Each ingredient")

    @staticmethod
    def validate_numeric_fields(experience: Any, cookingtime: Any) -> None:
        """ Validate experience and cookingtime fields for furnace recipes. """
        if not isinstance(experience, (float, int)):
            raise ValueError("Experience must be a float or int")
        if not isinstance(cookingtime, int):
            raise ValueError("Cookingtime must be an int")

    @staticmethod
    def validate_string_field(value: Any, field_name: str) -> None:
        """ Validate that a field is a string. """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")


# Crafting Recipes
@dataclass
class CraftingShapedRecipe(RecipeBase):
    """ Recipe for shaped crafting.

    >>> from stewbeet import *
    >>> recipe = CraftingShapedRecipe(
    ...     shape=["II", "CC", "CC"],
    ...     ingredients={"I":Ingr("minecraft:iron_ingot"), "C": Ingr("simplunium_ingot")}
    ... )
    >>> recipe.shape
    ['II', 'CC', 'CC']
    >>> recipe.ingredients['I']
    {'item': 'minecraft:iron_ingot'}
    >>> recipe.ingredients['C']
    {'components': {'minecraft:custom_data': {'your_namespace': {'simplunium_ingot': True}}}}

    Shape exceeding 3 rows raises ValueError:
    >>> try:
    ...     CraftingShapedRecipe(shape=["I", "I", "I", "I"], ingredients={"I": Ingr("minecraft:iron_ingot")})
    ... except ValueError as e:
    ...     "3 rows" in str(e)
    True

    Symbol defined in ingredients but absent from shape raises ValueError:
    >>> try:
    ...     CraftingShapedRecipe(shape=["II"], ingredients={"I": Ingr("minecraft:iron_ingot"), "X": Ingr("minecraft:gold_ingot")})
    ... except ValueError as e:
    ...     "must appear in the shape" in str(e)
    True

    Rows with inconsistent lengths raise ValueError:
    >>> try:
    ...     CraftingShapedRecipe(shape=["II", "I"], ingredients={"I": Ingr("minecraft:iron_ingot")})
    ... except ValueError as e:
    ...     "same number of columns" in str(e)
    True
    """
    shape: list[str]
    """ The shape pattern for the crafting recipe. """
    ingredients: dict[str, Ingr]
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
            self.validate_ingredient(ingredient, f"Ingredient for symbol '{symbol}'")
            if not any(symbol in line for line in self.shape):
                raise ValueError(f"Symbol '{symbol}' must appear in the shape")



@dataclass
class CraftingShapelessRecipe(RecipeBase):
    """ Recipe for shapeless crafting.

    >>> from stewbeet import *
    >>> recipe = CraftingShapelessRecipe(ingredients=[Ingr("minecraft:iron_ingot"), Ingr("minecraft:copper_ingot")])
    >>> len(recipe.ingredients)
    2
    >>> recipe.type
    'crafting_shapeless'

    Non-list ingredients raises ValueError:
    >>> try:
    ...     CraftingShapelessRecipe(ingredients=Ingr("minecraft:iron_ingot"))  # type: ignore[arg-type]
    ... except ValueError as e:
    ...     "must be a list" in str(e)
    True
    """
    ingredients: list[Ingr]
    """ List of ingredient specifications for shapeless crafting. """

    type = "crafting_shapeless"

    def __post_init__(self) -> None:
        self.type = "crafting_shapeless"
        super().__post_init__()
        self.validate_ingredients_list(self.ingredients)


# Furnace Recipes
@dataclass
class SmeltingRecipe(RecipeBase):
    """ Recipe for smelting in a furnace.

    >>> from stewbeet import *
    >>> recipe = SmeltingRecipe(ingredient=Ingr("minecraft:iron_ore"), experience=0.7, cookingtime=200)
    >>> recipe.experience
    0.7
    >>> recipe.cookingtime
    200

    Non-numeric experience raises ValueError:
    >>> try:
    ...     SmeltingRecipe(ingredient=Ingr("minecraft:iron_ore"), experience="high", cookingtime=200)  # type: ignore[arg-type]
    ... except ValueError as e:
    ...     "Experience must be a float or int" in str(e)
    True

    Non-integer cookingtime raises ValueError:
    >>> try:
    ...     SmeltingRecipe(ingredient=Ingr("minecraft:iron_ore"), experience=0.7, cookingtime=1.5)  # type: ignore[arg-type]
    ... except ValueError as e:
    ...     "Cookingtime must be an int" in str(e)
    True
    """
    ingredient: Ingr
    """ The ingredient to be smelted. """
    experience: float = 0.0
    """ Experience points awarded when the recipe is used. """
    cookingtime: int = 200
    """ Cooking time in ticks (200 ticks = 10 seconds by default). """

    type = "smelting"

    def __post_init__(self) -> None:
        self.type = "smelting"
        super().__post_init__()
        self.validate_ingredient(self.ingredient)
        self.validate_numeric_fields(self.experience, self.cookingtime)


@dataclass
class BlastingRecipe(RecipeBase):
    """ Recipe for blasting in a blast furnace.

    >>> from stewbeet import *
    >>> recipe = BlastingRecipe(ingredient=Ingr("minecraft:iron_ore"), experience=0.7, cookingtime=100)
    >>> recipe.experience
    0.7
    >>> recipe.cookingtime
    100
    """
    ingredient: Ingr
    """ The ingredient to be blasted. """
    experience: float = 0.0
    """ Experience points awarded when the recipe is used. """
    cookingtime: int = 100
    """ Cooking time in ticks (100 ticks = 5 seconds by default). """

    type = "blasting"

    def __post_init__(self) -> None:
        self.type = "blasting"
        super().__post_init__()
        self.validate_ingredient(self.ingredient)
        self.validate_numeric_fields(self.experience, self.cookingtime)


@dataclass
class SmokingRecipe(RecipeBase):
    """ Recipe for smoking in a smoker.

    >>> from stewbeet import *
    >>> recipe = SmokingRecipe(ingredient=Ingr("minecraft:chicken"), experience=0.35, cookingtime=100)
    >>> recipe.experience
    0.35
    >>> recipe.cookingtime
    100
    """
    ingredient: Ingr
    """ The ingredient to be smoked. """
    experience: float = 0.0
    """ Experience points awarded when the recipe is used. """
    cookingtime: int = 100
    """ Cooking time in ticks (100 ticks = 5 seconds by default). """

    type = "smoking"

    def __post_init__(self) -> None:
        self.type = "smoking"
        super().__post_init__()
        self.validate_ingredient(self.ingredient)
        self.validate_numeric_fields(self.experience, self.cookingtime)


@dataclass
class CampfireCookingRecipe(RecipeBase):
    """ Recipe for cooking on a campfire.

    >>> from stewbeet import *
    >>> recipe = CampfireCookingRecipe(ingredient=Ingr("minecraft:chicken"), experience=0.35, cookingtime=600)
    >>> recipe.experience
    0.35
    >>> recipe.cookingtime
    600
    """
    ingredient: Ingr
    """ The ingredient to be cooked. """
    experience: float
    """ Experience points awarded when the recipe is used. """
    cookingtime: int
    """ Cooking time in ticks (600 ticks = 30 seconds by default). """

    type = "campfire_cooking"

    def __post_init__(self) -> None:
        self.type = "campfire_cooking"
        super().__post_init__()
        self.validate_ingredient(self.ingredient)
        self.validate_numeric_fields(self.experience, self.cookingtime)


# Smithing Recipes
@dataclass
class SmithingTransformRecipe(RecipeBase):
    """ Recipe for smithing table transformation.

    >>> from stewbeet import *
    >>> recipe = SmithingTransformRecipe(
    ...     template=Ingr("minecraft:netherite_upgrade_smithing_template"),
    ...     base=Ingr("minecraft:diamond_sword"),
    ...     addition=Ingr("minecraft:netherite_ingot")
    ... )
    >>> recipe.template['item']
    'minecraft:netherite_upgrade_smithing_template'
    """
    template: Ingr
    """ The template item (e.g., upgrade template). """
    base: Ingr
    """ The base item to be transformed. """
    addition: Ingr
    """ The addition item (e.g., material). """

    type = "smithing_transform"

    def __post_init__(self) -> None:
        self.type = "smithing_transform"
        super().__post_init__()
        for name, ingredient in [("template", self.template), ("base", self.base), ("addition", self.addition)]:
            self.validate_ingredient(ingredient, name.capitalize())


@dataclass
class SmithingTrimRecipe(RecipeBase):
    """ Recipe for applying armor trims.

    >>> from stewbeet import *
    >>> recipe = SmithingTrimRecipe(
    ...     template=Ingr("minecraft:spire_armor_trim_smithing_template"),
    ...     base=Ingr("minecraft:netherite_chestplate"),
    ...     addition=Ingr("minecraft:diamond"),
    ...     pattern="minecraft:spire_armor_trim_smithing_template"
    ... )
    >>> recipe.addition['item']
    'minecraft:diamond'
    """
    template: Ingr
    """ The trim template. """
    base: Ingr
    """ The armor piece. """
    addition: Ingr
    """ The material for the trim. """
    pattern: str
    """ The trim pattern. """

    type = "smithing_trim"

    def __post_init__(self) -> None:
        self.type = "smithing_trim"
        super().__post_init__()
        for name, ingredient in [("template", self.template), ("base", self.base), ("addition", self.addition)]:
            self.validate_ingredient(ingredient, name.capitalize())
        self.validate_string_field(self.pattern, "Pattern")


# Other Recipes
@dataclass
class StonecuttingRecipe(RecipeBase):
    """ Recipe for stonecutting.

    >>> from stewbeet import *
    >>> recipe = StonecuttingRecipe(ingredient=Ingr("minecraft:stone"))
    >>> recipe.ingredient['item']
    'minecraft:stone'
    """
    ingredient: Ingr
    """ The ingredient to be cut. """

    type = "stonecutting"

    def __post_init__(self) -> None:
        self.type = "stonecutting"
        super().__post_init__()
        self.validate_ingredient(self.ingredient)


# Custom/Special Recipes
@dataclass
class PulverizingRecipe(RecipeBase):
    """ Custom recipe for SimplEnergy pulverizing.

    >>> from stewbeet import *
    >>> recipe = PulverizingRecipe(ingredient=Ingr("minecraft:iron_ore"))
    >>> recipe.ingredient['item']
    'minecraft:iron_ore'
    """
    ingredient: Ingr
    """ The ingredient to be pulverized. """

    type = "simplenergy_pulverizing"

    def __post_init__(self) -> None:
        self.type = "simplenergy_pulverizing"
        super().__post_init__()
        self.validate_ingredient(self.ingredient)


@dataclass
class AwakenedForgeRecipe(RecipeBase):
    """ Custom recipe for Stardust awakened forge.

    >>> from stewbeet import *
    >>> recipe = AwakenedForgeRecipe(ingredients=[Ingr("stardust_fragment"), Ingr("minecraft:iron_ingot")])
    >>> len(recipe.ingredients)
    2
    """
    ingredients: list[Ingr]
    """ List of ingredients for the awakened forge. """
    particle: str | None = None
    """ (Optional) Particle effect for the recipe. """

    type = "stardust_awakened_forge"

    def __post_init__(self) -> None:
        self.type = "stardust_awakened_forge"
        super().__post_init__()
        self.validate_ingredients_list(self.ingredients)


# Hardcoded Recipes (minimal implementation)
@dataclass
class HardcodedRecipe(RecipeBase):
    """Recipe for special/hardcoded crafting types.

    >>> recipe = HardcodedRecipe(type="crafting_special_armordye")
    >>> recipe.type
    'crafting_special_armordye'
    """
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
""" Type alias for all recipe types (CraftingShapedRecipe | CraftingShapelessRecipe | ...) """

