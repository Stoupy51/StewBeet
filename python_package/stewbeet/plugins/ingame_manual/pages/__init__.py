"""Page classes for the in-game manual."""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from .base import Page, Transformer
from .browser_page import CategoryBrowserPage
from .button_layout import ButtonLayout, Position
from .category_page import CategoryPage
from .custom_page import CustomPage
from .intro_page import IntroPage
from .item_page import ItemPage
from .raw_page import RawPage
from .texture_page import TexturePage

__all__ = [
	"ButtonLayout",
	"CategoryBrowserPage",
	"CategoryPage",
	"CustomPage",
	"IntroPage",
	"ItemPage",
	"Page",
	"Position",
	"RawPage",
	"TexturePage",
	"Transformer",
]
