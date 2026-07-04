"""The typed wiki button produced by the recipe renderer."""

# Imports
from dataclasses import dataclass

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ..refs import PageRef


@dataclass(kw_only=True)
class WikiButtonRender:
	""" A single wiki button (icon + hover) with a deferred click target.

	``blue_craft`` marks a craft that has no result (only ingredients), used by overflow
	handling. ``target`` is either a :class:`~..refs.PageRef` (resolved after page ordering)
	or a literal click-event dict (e.g. an author-provided ``open_url`` from a WikiButton).

	>>> button = WikiButtonRender(glyph="X", hover=["Some hover text"])
	>>> button.priority, button.target is None
	(1, True)
	"""
	glyph: str
	""" The font character drawn as the button icon. """
	hover: TextComponent
	""" Tooltip content shown when hovering the button. """
	target: PageRef | JsonDict | None = None
	""" Deferred page link, literal click event, or None for no click action. """
	blue_craft: bool = False
	""" True for crafts without a result (only ingredients); used by overflow handling. """
	priority: int = 1
	""" Higher priority buttons survive overflow trimming longer. """
	is_info: bool = False
	""" True for WikiButton info buttons (kept first, never treated as blue). """
