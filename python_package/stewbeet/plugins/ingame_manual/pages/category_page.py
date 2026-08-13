"""Category page: a clickable grid of the items in one category.

Ports the v1 ``encode_page`` category branch. The grid background (item "cases") is drawn
as a single 131px-tall bitmap glyph; clickable per-item glyphs are overlaid on top, each
linking to its item page via a deferred :class:`~..refs.PageRef`.
"""

# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import copy
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from PIL import Image

from ....core.utils.fonts import add_border, careful_resize
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
		config = manual.config
		name = self.title or self.anchor
		file_name = name.replace(" ", "_").replace("#", "").lower()
		simple_case = manual.simple_case

		page_font = manual.glyphs.allocate()
		manual.glyphs.add_provider(page_font, f"{config.project_id}:font/category/{file_name}.png", ascent=1, height=131)

		# Body starts with the manual-font base (shadow disabled for dialogs); the title is shown
		# by the dialog itself, so it is no longer part of the body.
		content: list[TextComponent] = []
		content.append({"text": "", "font": config.font, "color": "white", "shadow_color": [0,0,0,0]})
		content.append(SMALL_NONE_FONT * config.left_padding + page_font + "\n")

		page_image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
		x, y = 2, 2
		line: list[TextComponent] = []
		category_padding: list[str] = [VERY_SMALL_NONE_FONT]  # dialog-first

		max_items_reached = False
		for item in self.items:
			item_image = manual.load_item_texture(item)
			if not config.high_resolution:
				resized = careful_resize(item_image, 32)
			else:
				resized = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
				manual.images.high_res_icon(item, item_image)

			page_image.paste(simple_case, (x, y))
			page_image.paste(resized, (x + 2, y + 2), resized.convert("RGBA").split()[3])
			x += simple_case.size[0]

			component = manual.recipes.item_component(item)
			if not config.high_resolution:
				component["text"] = MEDIUM_NONE_FONT
			line.append(component)

			if len(line) == config.max_items_per_row:
				max_items_reached = True
				line.insert(0, SMALL_NONE_FONT * config.left_padding)
				content.extend(copy.deepcopy(line))
				content.extend(category_padding)
				for i in range(1, len(line)):
					selected = line[-i]
					if isinstance(selected, dict):
						selected["text"] = MEDIUM_NONE_FONT
				content.extend(["\n", *line, *category_padding, "\n"])
				line = []
				x = 2
				y += simple_case.size[1]

		if len(line) > 0:
			if max_items_reached:
				line.append(MEDIUM_NONE_FONT * max(0, config.max_items_per_row - len(line)))
			line.insert(0, SMALL_NONE_FONT * config.left_padding)
			content.extend(copy.deepcopy(line))
			content.extend(category_padding)
			for i in range(1, len(line)):
				selected = line[-i]
				if isinstance(selected, dict):
					selected["text"] = MEDIUM_NONE_FONT
			content.extend(["\n", *line, *category_padding, "\n"])

		page_image = add_border(page_image, manual.images.get_border_color(), BORDER_SIZE)
		os.makedirs(f"{config.font_cache_path}/category", exist_ok=True)
		page_image.save(f"{config.font_cache_path}/category/{file_name}.png")
		return content
