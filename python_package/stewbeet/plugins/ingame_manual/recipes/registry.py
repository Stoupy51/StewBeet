"""Recipe-type renderer base class and the global registry.

Each recipe type has one :class:`CraftRenderer` that owns *all* of its rendering: the main
page layout (:meth:`render_body`), the wiki-button hover lines (:meth:`append_hover`), its
human name (:attr:`name`), its high-res template glyph (:meth:`static_glyph`) and its
low-res image (:meth:`build_image`). Renderers register themselves into :data:`CRAFT_RENDERERS`
via :func:`register_craft_renderer`, so adding a recipe type is one new file + one call.

The ``r`` argument passed to renderer methods is the :class:`~.renderer.RecipeRenderer`
dispatcher, exposing ``r.config`` / ``r.glyphs`` / ``r.images`` / ``r.item_component(...)`` /
``r.append_or_invisible(...)`` / ``r.render_main(...)``.
"""

# ruff: noqa: E501
# Imports
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib import import_module
from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ....core.cls.ingredients import Ingr

if TYPE_CHECKING:
	from .renderer import RecipeRenderer


@dataclass(slots=True)
class CraftRenderer:
	""" Base class for a recipe-type renderer.

	Subclass it, set :attr:`types` (and optionally :attr:`name`), override the render
	methods you need, then call :func:`register_craft_renderer` on an instance.

	>>> class _EchoRenderer(CraftRenderer):
	...     types = ("test_echo",)
	...     name = "Echo"
	>>> _ = register_craft_renderer(_EchoRenderer())
	>>> get_craft_renderer("test_echo") is CRAFT_RENDERERS["test_echo"]
	True
	>>> get_craft_renderer("unknown_type") is None
	True
	>>> del CRAFT_RENDERERS["test_echo"]
	"""

	types: ClassVar[tuple[str, ...]] = ()
	""" The craft ``type`` strings this renderer handles. """
	name: ClassVar[str] = ""
	""" Human title shown in the wiki-button hover. Empty = no title line (e.g. crafting recipes). """

	def static_glyph(self, craft: JsonDict) -> str:
		""" The high-res template glyph for this craft (empty if the type has no template). """
		return ""

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		""" Append this craft's page layout to ``content``. Subclasses must implement.

		``add_change_page_to_ingr`` is the prologue flag controlling whether the single
		ingredient links to its page (used by furnace/linear layouts).
		"""
		raise NotImplementedError

	def append_hover(self, r: RecipeRenderer, craft: JsonDict, hover: list[TextComponent]) -> None:
		""" Append per-ingredient hover lines. Default: a single ``- x1 <ingredient>`` line. """
		hover.append({"text": "\n- x1 ", "color": "gray"})
		hover.append({"text": Ingr(craft["ingredient"]).to_name(), "color": "gray"})

	def build_image(self, r: RecipeRenderer, name: str, page_font: str, craft: JsonDict, output_name: str = "") -> None:
		""" Generate the low-resolution recipe PNG (no-op for types that don't need one). """
		return None


# Global registry: craft type string -> renderer instance.
CRAFT_RENDERERS: dict[str, CraftRenderer] = {}
""" Registry of all craft renderers, by craft type. """

BUILTIN_RENDERER_MODULES: tuple[str, ...] = ("awakened_forge", "furnace", "linear", "shaped", "smithing")
""" Modules under .types that register the built-in renderers when they execute. """


def register_craft_renderer(renderer: CraftRenderer) -> CraftRenderer:
	""" Register ``renderer`` for each of its :attr:`~CraftRenderer.types`. Returns it. """
	for craft_type in renderer.types:
		CRAFT_RENDERERS[craft_type] = renderer
	return renderer


@cache
def load_builtin_renderers() -> dict[str, CraftRenderer]:
	""" Import the built-in renderer modules once, then return the populated registry.

	Those modules register themselves as a side effect of executing, which under PEP 810 never
	happens on its own since nothing imports them by name. Every lookup goes through here instead
	of relying on the package import that used to pull them in eagerly.

	Returns:
		dict[str, CraftRenderer]: The registry, with every built-in renderer present

	Examples:
		>>> "crafting_shaped" in load_builtin_renderers()
		True
	"""
	for name in BUILTIN_RENDERER_MODULES:
		import_module(f"{__name__.rsplit('.', 1)[0]}.types.{name}")
	return CRAFT_RENDERERS


def get_craft_renderer(craft_type: str) -> CraftRenderer | None:
	""" Return the renderer registered for ``craft_type`` (or None). """
	return load_builtin_renderers().get(craft_type)

