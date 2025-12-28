
# Imports
from dataclasses import dataclass

from beet.core.utils import TextComponent

from ._utils import StMapping
from .item import Item


@dataclass(kw_only=True)
class PaintingData(StMapping):
    """ Data class for painting-specific data.
    {
        "texture": "stewbeet_painting_2x2",            # Default to item id if not given (this example links to "assets/textures/stewbeet_painting_2x2.png")
        "author": {"text":"Stoupy","color":"yellow"},  # Author defaults to ctx.project_author if not given
        "title": {"text":"Da' Icon","color":"gray"},   # Title defaults to item name if not given
        "width": 2, "height": 2
    }
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

