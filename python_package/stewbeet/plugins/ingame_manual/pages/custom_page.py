""" A free-form page: arbitrary Minecraft text components, unrelated to any item. """

# Imports
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from .base import Page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True, slots=True)
class CustomPage(Page):
	""" A page with a developer-supplied component body and optional extra glyphs.

	``declared_glyphs`` lets a page ship its own bitmap providers
	(each a dict with ``char``/``file``/``ascent``/``height``);
	they are registered at build time.

	>>> page = CustomPage(anchor="welcome", title="Welcome", body=[{"text": "Hi"}])
	>>> page.build(None)  # neutral base first, then the developer body untouched
	[{'text': '', 'shadow_color': [0, 0, 0, 0]}, {'text': 'Hi'}]
	"""
	body: list[TextComponent] = field(default_factory=list[TextComponent])
	""" The page content, as a list of Minecraft text components. """
	declared_glyphs: list[JsonDict] = field(default_factory=list[JsonDict])
	""" Optional glyphs to register at build time. """

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Register the declared glyphs, then return the body under a neutral (no-font) base. """
		for g in self.declared_glyphs:
			manual.glyphs.add_provider(g["char"], g["file"], g["ascent"], g["height"])
		# Neutral base (default font, no shadow); the body keeps its own fonts/colors. The manual
		# font is NOT forced here, and the title is shown by the dialog itself.
		content: list[TextComponent] = [{"text": "", "shadow_color": [0,0,0,0]}]
		content += list(self.body)
		return content

