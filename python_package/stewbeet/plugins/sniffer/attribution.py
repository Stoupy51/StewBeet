
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Generator
from contextlib import contextmanager
from typing import Protocol

from ...core.__memory__ import Mem
from .model import AttributionScope, SourceOrigin


# Classes
class Declared(Protocol):
	""" Anything carrying the origin captured when it was declared, in practice an Item or a Block. """
	origin: SourceOrigin | None


# Functions
@contextmanager
def attribute_to(definition: Declared) -> Generator[None]:
	""" Attribute everything written inside this scope to a declaration's own site.

	Needed because a plugin generating from `Mem.definitions` has no project frame on the stack at
	all: the declaration returned long before, leaving only beet's pipeline and the user's entry
	point above the write. The declaration captured its own origin when it was constructed, and
	this hands that origin to every write inside the block.

	Nothing in StewBeet enters this scope yet; wiring it into the generation loops is step B2. Until
	then plugin-generated content resolves to tier 3 and is emitted unmapped, which is correct.

	>>> from stewbeet.plugins.sniffer.model import SourceOrigin
	>>> class Fake: origin = SourceOrigin(file="/p/blocks.py", line=11, column=0)
	>>> with attribute_to(Fake()):
	...     Mem.attribution[-1].origin.line
	11
	>>> Mem.attribution
	[]
	"""
	origin: SourceOrigin | None = definition.origin
	if origin is None:
		yield
		return

	Mem.attribution.append(AttributionScope(origin=origin))
	try:
		yield
	finally:
		Mem.attribution.pop()

