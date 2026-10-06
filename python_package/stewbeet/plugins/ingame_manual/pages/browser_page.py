"""Category browser page: a clickable grid linking to each category page."""

# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from dataclasses import dataclass
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ..refs import PageRef
from .base import Page
from .category_page import CategoryPage, grid_page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True, slots=True)
class CategoryBrowserPage(Page):
	""" The "Category browser" page: one clickable cell per category page. """

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Draw the case-grid background glyph and overlay one clickable cell per category page, showing its first item. """
		categories: list[CategoryPage] = [p for p in manual.pages if isinstance(p, CategoryPage) and p.items]

		def link_to_category(index: int, component: JsonDict) -> None:
			component.setdefault("hover_event", {}).setdefault("components", {})
			component["hover_event"]["components"]["item_name"] = {"text": categories[index].title, "color": "white"}
			component["click_event"] = {"action": "change_page", "page": PageRef(anchor=categories[index].anchor)}

		return grid_page(manual, "categories_page", [category.items[0] for category in categories], link_to_category)

