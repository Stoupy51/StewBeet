"""A pre-built page: passes a ready list of text components straight through.

Used for special pages whose content is produced elsewhere (e.g. the ported
``stardust_forge`` page in :mod:`..special`).
"""

# Imports
import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from beet.core.utils import TextComponent

from .base import Page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True, slots=True)
class RawPage(Page):
	""" A page that simply yields its pre-built ``content``.

	>>> RawPage(anchor="forge", content=["hello"]).build(None)
	['hello']
	"""
	content: list[TextComponent] = field(default_factory=list[TextComponent])
	""" The ready-made dialog body, deep-copied at build time. """

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Return a deep copy of ``content`` (so later passes cannot mutate the original). """
		return copy.deepcopy(self.content)
