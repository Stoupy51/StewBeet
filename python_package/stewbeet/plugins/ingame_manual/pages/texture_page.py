"""A page whose body is a custom background texture, optionally with text baked into it.

This is the feature that lets developers ship "different textures for different pages and
the text/descriptions on the texture itself": supply a background image (path or PIL
image) and a list of :class:`~..images.BakedText` drawn onto it via PIL. The composited
image is registered as a single full-page glyph; optional Minecraft ``body`` components can
be added underneath (e.g. clickable links).
"""

# Imports
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from PIL import Image

from ....core.__memory__ import Mem
from ..images import BakedText
from .base import Page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True)
class TexturePage(Page):
	""" A full-texture page with optional baked-in text and trailing MC components.

	Attributes:
		background	(str|Image.Image):	Background image path, or a ready PIL image.
		baked_texts	(list[BakedText]):	Texts drawn onto the background with PIL.
		body		(list[TextComponent]):	Optional MC text shown under the texture.
		glyph_ascent / glyph_height	(int):	Bitmap placement of the page texture (size and Y offset).
		left_padding / right_padding	(int):	Invisible pixels emitted before/after the texture glyph.
						The dialog centers the line, so ``left_padding`` shifts the texture right
						and ``right_padding`` shifts it left, each by half the padding.
	"""
	background: str | Image.Image = ""
	baked_texts: list[BakedText] = field(default_factory=list[BakedText])
	body: list[TextComponent] = field(default_factory=list[TextComponent])
	glyph_ascent: int = 1
	glyph_height: int = 131
	left_padding: int = 0
	right_padding: int = 0

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Composite the background + baked texts, register it as one glyph, append the body. """
		config = manual.config
		if isinstance(self.background, str):
			Mem.used_textures.add(self.background)  # the file is re-encoded under a new name, mark the source as used
			bg = Image.open(self.background)
		else:
			bg = self.background
		composited = manual.images.bake_text_onto(bg, self.baked_texts) if self.baked_texts else bg.convert("RGBA")

		glyph_name = self.anchor.replace(":", "_").replace(" ", "_").lower()
		page_font = manual.images.register_full_page_glyph(composited, glyph_name, ascent=self.glyph_ascent, height=self.glyph_height)
		page_text: str = manual.images.invisible_spacer(self.left_padding) + page_font + manual.images.invisible_spacer(self.right_padding)

		# Neutral base (default font, no shadow) so the developer body keeps its own font; only the
		# page-texture glyph is drawn in the manual font. The title is shown by the dialog itself.
		content: list[TextComponent] = [{"text": "", "shadow_color": [0,0,0,0]}]
		content.append({"text": page_text + "\n", "font": config.font, "color": "white"})
		content += list(self.body)
		return content
