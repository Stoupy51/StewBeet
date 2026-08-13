"""Recipe rendering package.

Re-exports the dispatcher and the public registry surface. Existing call sites keep importing
from ``..recipes``. The built-in type renderers load on first lookup rather than on import, see
:func:`~.registry.load_builtin_renderers`.
"""

from . import types
from .buttons import WikiButtonRender
from .collection import convert_shapeless_to_shaped
from .registry import CRAFT_RENDERERS, CraftRenderer, get_craft_renderer, load_builtin_renderers, register_craft_renderer
from .renderer import RecipeRenderer

__all__ = [
	"CRAFT_RENDERERS",
	"CraftRenderer",
	"RecipeRenderer",
	"WikiButtonRender",
	"convert_shapeless_to_shaped",
	"get_craft_renderer",
	"load_builtin_renderers",
	"register_craft_renderer",
	"types",
]
