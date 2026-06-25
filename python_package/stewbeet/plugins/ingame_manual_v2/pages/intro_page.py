"""Introduction page: manual title, project logo, and the configurable first-page text."""

# Imports
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from PIL import Image

from ...initialize.source_lore_font import find_pack_png
from ..glyphs import MEDIUM_NONE_FONT
from ..images import careful_resize
from .base import Page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True)
class IntroPage(Page):
	""" The first page: manual name, logo glyph, then the project's intro text. """

	def build(self, manual: Manual) -> list[TextComponent]:
		config = manual.config
		use_dialog = config.use_dialog > 0

		page_font = manual.glyphs.allocate()
		manual.glyphs.add_provider(page_font, f"{config.project_id}:font/page/_logo.png", ascent=0, height=40)

		# Manual-font base (shadow disabled for dialogs); the manual name is shown as the dialog title.
		content: list[TextComponent] = [{"text": "", "font": config.font, "color": "white", "shadow_color": [0,0,0,0]}]
		content.append({"text": MEDIUM_NONE_FONT * (0 if use_dialog else 2) + page_font})

		# Build the logo image from pack.png
		icon_path = find_pack_png()
		assert icon_path and os.path.exists(icon_path), "Missing pack.png in your working tree (needed for the manual)"
		logo = careful_resize(Image.open(icon_path), 256)
		os.makedirs(f"{config.cache_path}/font/page", exist_ok=True)
		logo.save(f"{config.cache_path}/font/page/_logo.png")

		content.append({"text": "\n" * 6})
		content.append([{"text": "", "font": "minecraft:default", "color": "black"}, config.first_page_text])
		return content
