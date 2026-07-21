
# Imports
from dataclasses import dataclass

from beet import PaintingVariant, Texture
from beet.core.utils import TextComponent

from ._utils import StMapping
from .item import Item
from .resource import Resource


@dataclass(kw_only=True, slots=True)
class PaintingData(StMapping):
    """ Data class for painting-specific data.

    >>> pd = PaintingData(
    ...     texture="stewbeet_painting_2x2",            # Default to item id if not given (this example links to "assets/textures/stewbeet_painting_2x2.png")
    ...     author={"text":"Stoupy","color":"yellow"},  # Author defaults to ctx.project_author if not given
    ...     title={"text":"Da' Icon","color":"gray"},   # Title defaults to item name if not given
    ...     width=4,
    ...     height=3
    ... )
    """
    texture: str | None = None
    """ Texture identifier for the painting. Defaults to item id if not provided. """
    author: TextComponent | None = None
    """ Author of the painting. Defaults to ctx.project_author if not provided. """
    title: TextComponent | None = None
    """ Title of the painting. Defaults to item name if not provided. """
    width: int
    """ Width of the painting in blocks. """
    height: int
    """ Height of the painting in blocks. """

# Class
@dataclass(kw_only=True, slots=True)
class Painting(Item):
    """ Represents a custom painting item.

    ### Texture will default to "stewbeet_painting_2x2", author and title will default accordingly
    >>> my_painting = Painting(
    ...     id="stewbeet_painting_2x2",
    ...     painting_data=PaintingData(
    ...         author={"text":"An Artist I would say","color":"yellow"},
    ...         width=2,
    ...         height=2
    ...     ),
    ...     recipes=[],
    ...     components={
    ...         "max_stack_size": 16
    ...     }
    ... )
    >>> my_painting
    Painting(id='stewbeet_painting_2x2', base_item='minecraft:painting', manual_category=None, recipes=[], override_model=None, hand_model=None, override_model_contexts=None, wiki_buttons=None, components={'max_stack_size': 16, 'painting/variant': 'your_namespace:stewbeet_painting_2x2'}, skip_gives=False, painting_data=PaintingData(texture='stewbeet_painting_2x2', author={'text': 'An Artist I would say', 'color': 'yellow'}, title={'text': 'Stewbeet Painting 2X2'}, width=2, height=2))

    ### Resource locations
    >>> my_painting.variant
    'your_namespace:stewbeet_painting_2x2'
    >>> my_painting.painting_texture
    'your_namespace:painting/stewbeet_painting_2x2'
    >>> my_painting.asset_id
    'your_namespace:stewbeet_painting_2x2'
    """  # noqa: E501
    base_item: str = "minecraft:painting"
    painting_data: PaintingData

    def __post_init__(self) -> None:
        from ..__memory__ import Mem
        if self.painting_data.texture is None:
            self.painting_data.texture = self.id
        if self.painting_data.author is None:
            self.painting_data.author = Mem.ctx.project_author
        if self.painting_data.title is None:
            self.painting_data.title = {"text": self.id.replace("_", " ").title()}

        # Ensure the painting variant is set in components
        if "painting/variant" not in self.components:
            self.components["painting/variant"] = f"{Mem.ctx.project_id}:{self.id}"

        # Call the parent post-init to register the item
        super().__post_init__()

    # Resource locations
    @property
    def variant(self) -> Resource[PaintingVariant]:
        """ The painting variant of this painting, honoring the "painting/variant" component when set. """
        override: str | None = self.components.get("painting/variant")
        if override:
            return Resource(PaintingVariant, override)
        return Resource(PaintingVariant, self.id)

    @property
    def painting_texture(self) -> Resource[Texture]:
        """ The texture of this painting, ex: "your_namespace:painting/stewbeet_painting_2x2". """
        return Resource(Texture, f"painting/{self.painting_data.texture or self.id}")

    @property
    def asset_id(self) -> str:
        """ The asset_id referenced by the painting variant, ex: "your_namespace:stewbeet_painting_2x2".

        Beware: this is NOT the texture resource location. Minecraft resolves a painting asset_id of
        "ns:name" to "assets/ns/textures/painting/name.png", so the two strings differ.
        """
        return f"{self.painting_texture.namespace}:{self.painting_data.texture or self.id}"

