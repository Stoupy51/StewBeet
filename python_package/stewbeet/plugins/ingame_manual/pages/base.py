"""The :class:`Page` base class and lifecycle.

A page is a self-contained unit that knows how to render itself directly to a dialog body:
a list of Minecraft text components where element 0 is the parent whose style (notably its
font) cascades to the siblings. Subclasses implement :meth:`build`; the base :meth:`render`
wraps it and applies developer ``transformers`` last, so per-item/page overrides compose cleanly.
"""

# Imports
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent
from PIL import Image

from ..button_layout import ButtonLayout

if TYPE_CHECKING:
	from ..manual import Manual


# A transformer mutates/returns a page's content right before it is finalized.
Transformer = Callable[[list[TextComponent], "Manual"], list[TextComponent]]


@dataclass(kw_only=True, slots=True)
class Page:
	""" Base class for every manual page.

	>>> page = Page(anchor="demo", transformers=[lambda content, manual: [*content, "!"]])
	>>> page.render(None)  # the default build() yields [], then transformers run in order
	['!']
	"""
	anchor: str
	""" Stable identity used for ordering and deferred links (e.g. "intro", "category:Materials",
	"item:wrench"). Must be unique within a manual. """
	title: str = ""
	""" Human-readable page title. """
	item_id: str | None = None
	""" If this page represents an item, its id (drives ``PageRef(item=...)`` resolution and
	dialog atlas sprites). """
	button_layout: ButtonLayout | None = None
	""" Per-page override of the manual-wide button layout. """
	book_texture: str | Image.Image | None = None
	""" Per-page override of the book background ("book.png"). A path (project path, or a filename
	resolved against the templates dir so ``manual_overrides`` files work) or a ready PIL image.
	None = shared book. """
	book_font: str = field(default="", init=False, repr=False)
	""" Glyph char registered for :attr:`book_texture` (set during emit, "" = shared BOOK_FONT). """
	home_texture: str | Image.Image | None = None
	""" Per-page override of the home button ("home.png"), same accepted values as ``book_texture``.
	Keep the default's 16x16 proportions so the navigation row stays aligned. None = shared home. """
	home_font: str = field(default="", init=False, repr=False)
	""" Glyph char registered for :attr:`home_texture` (set during emit, "" = shared HOME_FONT). """
	home_button: bool = True
	""" Whether this page shows the home button in its navigation row (an invisible spacer keeps the
	prev/next layout when hidden). The first page never shows it regardless of this flag. """
	transformers: list[Transformer] = field(default_factory=list[Transformer])
	""" Developer hooks applied to the rendered content, in order. """
	optimize: bool = True
	""" Whether the optimizer may merge this page's components. Set False for pre-built
	content whose element positions are significant (e.g. a RawPage relying on absolute indices). """

	def prepare(self, manual: Manual) -> None:
		""" Heavy, order-independent setup (collect data, allocate glyphs). Default: no-op. """
		return None

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Produce the raw page content. Subclasses override this. """
		return []

	def render(self, manual: Manual) -> list[TextComponent]:
		""" Build the page then apply ``transformers`` (last), returning final content. """
		content = self.build(manual)
		for transform in self.transformers:
			content = transform(content, manual)
		return content

	def resolve_button_layout(self, manual: Manual) -> ButtonLayout:
		""" Return this page's effective button layout (own override or manual default). """
		return self.button_layout if self.button_layout is not None else manual.config.button_layout

