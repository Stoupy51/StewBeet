"""Category page: a clickable grid of the items in one category.

The grid background (item "cases") is drawn as a single 131px-tall bitmap glyph;
clickable per-item glyphs are overlaid on top, each linking to its item page via a deferred :class:`~..refs.PageRef`.
"""

# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import copy
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ....core.utils.fonts import add_border, careful_resize, save_png
from ..glyphs import BORDER_SIZE, MEDIUM_NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT
from .base import Page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True, slots=True)
class CategoryPage(Page):
	""" A page showing every item of one category as a clickable grid. """
	items: list[str] = field(default_factory=list[str])

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Draw the case-grid background glyph and overlay one clickable component per item. """
		file_name: str = (self.title or self.anchor).replace(" ", "_").replace("#", "").lower()
		return grid_page(manual, file_name, self.items)


def grid_page(
	manual: Manual, file_name: str, items: list[str], decorate: Callable[[int, JsonDict], None] | None = None,
) -> list[TextComponent]:
	""" A page of item cases over the glyph `font/category/<file_name>.png`, each case overlaid with its item's component.

	Args:
		decorate: Called with each item's index and component before the component is laid out, to change what it shows or does.
	"""
	config = manual.config
	simple_case = manual.simple_case
	page_font = manual.glyphs.allocate()
	manual.glyphs.add_provider(page_font, f"{config.project_id}:font/category/{file_name}.png", ascent=1, height=131)

	# The title is shown by the dialog itself, so the body starts with the manual-font base, shadow disabled
	content: list[TextComponent] = [
		{"text": "", "font": config.font, "color": "white", "shadow_color": [0,0,0,0]},
		SMALL_NONE_FONT * config.left_padding + page_font + "\n",
	]
	page_image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
	line: list[TextComponent] = []
	rows: int = 0
	for index, item in enumerate(items):
		item_image = manual.load_item_texture(item)
		if not config.high_resolution:
			resized = careful_resize(item_image, 32)
		else:
			resized = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
			manual.images.high_res_icon(item, item_image)
		x, y = 2 + len(line) * simple_case.size[0], 2 + rows * simple_case.size[1]
		page_image.paste(simple_case, (x, y))
		page_image.paste(resized, (x + 2, y + 2), resized.convert("RGBA").split()[3])

		component = manual.recipes.item_component(item)
		if decorate is not None:
			decorate(index, component)
		if not config.high_resolution:
			component["text"] = MEDIUM_NONE_FONT
		line.append(component)
		if len(line) == config.max_items_per_row:
			content += grid_row(line, config.left_padding)
			line = []
			rows += 1

	if line:
		if rows:
			line.append(MEDIUM_NONE_FONT * max(0, config.max_items_per_row - len(line)))
		content += grid_row(line, config.left_padding)

	page_image = add_border(page_image, manual.images.get_border_color(), BORDER_SIZE)
	os.makedirs(f"{config.font_cache_path}/category", exist_ok=True)
	save_png(page_image, f"{config.font_cache_path}/category/{file_name}.png")
	return content


def grid_row(line: list[TextComponent], left_padding: int) -> list[TextComponent]:
	""" One row of the grid, written twice: once with the item glyphs, then again with each clickable cell blank, laid over them. """
	line = [SMALL_NONE_FONT * left_padding, *line]
	shown: list[TextComponent] = copy.deepcopy(line)
	for selected in line[1:]:
		if isinstance(selected, dict):
			selected["text"] = MEDIUM_NONE_FONT
	return [*shown, VERY_SMALL_NONE_FONT, "\n", *line, VERY_SMALL_NONE_FONT, "\n"]

