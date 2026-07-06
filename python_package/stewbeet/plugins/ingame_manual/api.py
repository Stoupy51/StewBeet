""" Public API surface for ingame_manual (re-exported from the top-level ``stewbeet``).

Developers use :func:`get_manual` in their setup to grab the live :class:`Manual` and
register pages/hooks before the plugin builds it.
"""

# Imports
from .config import ManualConfig
from .images import BakedText
from .manual import Manual, Phase
from .pages import (
	ButtonLayout,
	CategoryBrowserPage,
	CategoryPage,
	CustomPage,
	IntroPage,
	ItemPage,
	Page,
	RawPage,
	TexturePage,
)
from .paths import template_path
from .recipes import CraftRenderer, WikiButtonRender, register_craft_renderer
from .refs import PageRef

__all__ = [
	"BakedText",
	"ButtonLayout",
	"CategoryBrowserPage",
	"CategoryPage",
	"CraftRenderer",
	"CustomPage",
	"IntroPage",
	"ItemPage",
	"Manual",
	"ManualConfig",
	"Page",
	"PageRef",
	"Phase",
	"RawPage",
	"TexturePage",
	"WikiButtonRender",
	"get_manual",
	"register_craft_renderer",
	"template_path",
]


def get_manual() -> Manual:
	""" Return the current :class:`Manual`, creating it from the beet meta if needed.

	Call this in ``setup_definitions`` (after items are defined) to register custom pages,
	hooks (``manual.on(...)`` / ``manual.on_item_page(...)``) and button layouts. The
	ingame_manual plugin reuses the same handle when it runs.
	"""
	from ...core.__memory__ import Mem
	if Mem.manual is None:
		Mem.manual = Manual(ManualConfig.from_meta(Mem.ctx))
	return Mem.manual

