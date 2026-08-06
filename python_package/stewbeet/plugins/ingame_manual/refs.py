"""Deferred page links.

A :class:`PageRef` represents "a link to some page" without committing to a concrete page
number. Links are emitted during rendering and substituted in a single pass by
``Manual.resolve()`` *after* the page order is final. So inserting/reordering/replacing
pages never requires the manual ``+1`` page-number bumping the v1 plugin needed.
"""

# Imports
from dataclasses import dataclass


@dataclass(slots=True)
class PageRef:
	""" A deferred reference to a manual page.

	Exactly one of the targeting fields is meaningful, checked in order:
	``item`` (link to the page generated for an item id), then ``anchor`` (link to a page
	by its stable anchor), then ``page`` (a literal 1-based page index).

	>>> PageRef(item="wrench").item
	'wrench'
	>>> PageRef(anchor="category:Materials").anchor
	'category:Materials'
	>>> PageRef(page=3).page
	3
	"""
	item: str | None = None
	anchor: str | None = None
	page: int | None = None
