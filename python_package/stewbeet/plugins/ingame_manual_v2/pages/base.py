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

from ..button_layout import ButtonLayout

if TYPE_CHECKING:
	from ..manual import Manual


# A transformer mutates/returns a page's content right before it is finalized.
Transformer = Callable[[list[TextComponent], "Manual"], list[TextComponent]]


@dataclass(kw_only=True)
class Page:
	""" Base class for every manual page.

	Attributes:
		anchor			(str):	Stable identity used for ordering and deferred links (e.g. "intro",
						"category:Materials", "item:wrench"). Must be unique within a manual.
		title			(str):	Human-readable page title.
		item_id			(str|None):	If this page represents an item, its id (drives ``PageRef(item=...)``
						resolution and dialog atlas sprites).
		button_layout	(ButtonLayout|None):	Per-page override of the manual-wide button layout.
		transformers	(list):	Developer hooks applied to the rendered content, in order.
	"""
	anchor: str
	title: str = ""
	item_id: str | None = None
	button_layout: ButtonLayout | None = None
	transformers: list[Transformer] = field(default_factory=list[Transformer])
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
