"""Category browser page: a clickable grid linking to each category page."""

# Imports
import copy
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ..glyphs import BORDER_SIZE, MEDIUM_NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT
from ..images import add_border, careful_resize
from ..refs import PageRef
from .base import Page
from .category_page import CategoryPage

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True)
class CategoryBrowserPage(Page):
	""" The "Category browser" page: one clickable cell per category page. """

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Draw the case-grid background glyph and overlay one clickable cell per category page. """
		config = manual.config
		file_name = "categories_page"
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
		category_padding: list[str] = [VERY_SMALL_NONE_FONT]

		category_pages = [p for p in manual.pages if isinstance(p, CategoryPage)]
		max_items_reached = False
		for cat in category_pages:
			if not cat.items:
				continue
			item = cat.items[0]
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
			component.setdefault("hover_event", {}).setdefault("components", {})
			component["hover_event"]["components"]["item_name"] = {"text": cat.title, "color": "white"}
			component["click_event"] = {"action": "change_page", "page": PageRef(anchor=cat.anchor)}
			if not config.high_resolution:
				component["text"] = MEDIUM_NONE_FONT
			line.append(component)

			if len(line) == config.max_items_per_row:
				max_items_reached = True
				line.insert(0, SMALL_NONE_FONT * config.left_padding)
				content += [*copy.deepcopy(line), *category_padding, "\n"]
				for i in range(1, len(line)):
					selected = cast(JsonDict, line[-i])
					selected["text"] = MEDIUM_NONE_FONT
				content += [*line, *category_padding, "\n"]
				line = []
				x = 2
				y += simple_case.size[1]

		if len(line) > 0:
			if max_items_reached:
				line.append(MEDIUM_NONE_FONT * max(0, config.max_items_per_row - len(line)))
			line.insert(0, SMALL_NONE_FONT * config.left_padding)
			content += [*copy.deepcopy(line), *category_padding, "\n"]
			for i in range(1, len(line)):
				selected = line[-i]
				if isinstance(selected, dict):
					selected["text"] = MEDIUM_NONE_FONT
			content += [*line, *category_padding, "\n"]

		page_image = add_border(page_image, manual.images.get_border_color(), BORDER_SIZE)
		os.makedirs(f"{config.cache_path}/font/category", exist_ok=True)
		page_image.save(f"{config.cache_path}/font/category/{file_name}.png")
		return content
