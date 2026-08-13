"""Wiki-button placement configuration.

A :class:`ButtonLayout` decides *where* and *which* wiki buttons (small clickable
recipe-result / info icons) appear on a page, and how overflow is handled. It can be set
as the manual-wide default (``ManualConfig.button_layout``) or overridden per page
(``Page.button_layout``).

Lives at the package root (not under ``pages/``) so :mod:`..config` can import it without
triggering the ``pages`` package: which would create an import cycle.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# Runtime import (not just TYPE_CHECKING): the parametrized default_factory below evaluates
# list[WikiButtonRender] at class-definition time. recipes does not import button_layout, so
# this does not create an import cycle.
from .recipes import WikiButtonRender

# Where the button grid is placed inside a page's content: a known keyword or a callable
# ``(content, buttons, manual) -> content``.
Position = str  # "after_recipe" | "bottom" | "top" | callable


@dataclass(kw_only=True, slots=True)
class ButtonLayout:
	""" Controls wiki-button rendering for a page.

	>>> layout = ButtonLayout(columns=6, position="bottom")
	>>> layout.columns
	6
	"""
	columns: int = 5
	""" Number of buttons per row. """
	max_buttons: int = 20
	""" Hard cap on how many buttons are shown (overflow dropped by priority). """
	position: Position | Callable[..., Any] = "after_recipe"
	""" Where the button grid is spliced into the page content: "after_recipe" inserts it right
	after the main craft content (before anything appended later, e.g. special notes),
	"top" places it just under the title (before the recipe), "bottom" appends it at the very
	end of the page, and a callable ``(content, buttons, manual) -> content`` takes full control
	(it receives the un-rendered :class:`~.recipes.WikiButtonRender` list and must return the
	final content). """
	order: Callable[[WikiButtonRender], Any] | None = None
	""" Sort key applied to buttons before layout (e.g. ``lambda b: -b.priority``). """
	include: Callable[[WikiButtonRender], bool] | None = None
	""" Predicate ``(button) -> bool`` filtering which buttons to keep. """
	extra_buttons: list[WikiButtonRender] = field(default_factory=list[WikiButtonRender])
	""" Additional developer-supplied buttons appended before layout. """

	def clone(self) -> ButtonLayout:
		""" Return a shallow copy (so per-page overrides don't mutate the shared default).

		>>> layout = ButtonLayout(columns=4)
		>>> copy = layout.clone()
		>>> copy == layout, copy is layout
		(True, False)
		"""
		return ButtonLayout(
			columns=self.columns,
			max_buttons=self.max_buttons,
			position=self.position,
			order=self.order,
			include=self.include,
			extra_buttons=list(self.extra_buttons),
		)

