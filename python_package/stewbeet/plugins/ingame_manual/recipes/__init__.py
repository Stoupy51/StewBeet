"""Recipe rendering package.

Re-exports the dispatcher and the public registry surface, and imports the built-in type
renderers so they self-register. Existing call sites keep importing from ``..recipes``.
"""

from . import types  # side effect: importing the package registers the built-in renderers
from .buttons import WikiButtonRender
from .collection import convert_shapeless_to_shaped
from .registry import CRAFT_RENDERERS, CraftRenderer, get_craft_renderer, register_craft_renderer
from .renderer import RecipeRenderer

__all__ = [
	"CRAFT_RENDERERS",
	"CraftRenderer",
	"RecipeRenderer",
	"WikiButtonRender",
	"convert_shapeless_to_shaped",
	"get_craft_renderer",
	"register_craft_renderer",
	"types",
]
