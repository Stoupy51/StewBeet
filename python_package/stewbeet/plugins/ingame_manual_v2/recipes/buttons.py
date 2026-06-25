"""The typed wiki button produced by the recipe renderer."""

# Imports
from __future__ import annotations

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
	"""
	glyph: str
	hover: TextComponent
	target: PageRef | JsonDict | None = None
	blue_craft: bool = False
	priority: int = 1
	is_info: bool = False  # True for WikiButton info buttons (kept first, never treated as blue)
