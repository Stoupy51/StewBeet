
# Imports
from dataclasses import dataclass

from beet.core.utils import TextComponent

from ._utils import StMapping
from .item import Item


@dataclass(kw_only=True)
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
@dataclass(kw_only=True)
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
    Painting(id='stewbeet_painting_2x2', base_item='minecraft:painting', manual_category=None, recipes=[], override_model=None, hand_model=None, wiki_buttons=None, components={'max_stack_size': 16, 'painting/variant': 'your_namespace:stewbeet_painting_2x2'}, painting_data=PaintingData(texture='stewbeet_painting_2x2', author={'text': 'An Artist I would say', 'color': 'yellow'}, title={'text': 'Stewbeet Painting 2X2'}, width=2, height=2))
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
            ns = Mem.ctx.project_id if Mem.ctx else "your_namespace"
            self.components["painting/variant"] = f"{ns}:{self.id}"

        # Call the parent post-init to register the item
        super().__post_init__()

