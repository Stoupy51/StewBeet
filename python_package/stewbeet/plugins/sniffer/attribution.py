
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Generator, Iterable
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

	>>> from stewbeet.plugins.sniffer.model import SourceOrigin
	>>> class Fake: origin = SourceOrigin(file="/p/blocks.py", line=11, column=0)
	>>> with attribute_to(Fake()):
	...     Mem.attribution[-1].origin.line
	11
	>>> Mem.attribution
	[]
	"""
	origin: SourceOrigin | None = getattr(definition, "origin", None)
	if origin is None:
		yield
		return

	Mem.attribution.append(AttributionScope(origin=origin))
	try:
		yield
	finally:
		Mem.attribution.pop()



def attributed[T: Declared](definitions: Iterable[tuple[str, T]]) -> Generator[tuple[str, T]]:
	""" Iterate definitions, attributing everything each iteration writes to that declaration.

	A generation loop wraps its iterable in this instead of indenting its whole body into a `with`.
	The scope opens before the body runs and closes when the loop asks for the next item, or when it
	breaks and the generator is closed, so it always matches the iteration exactly.

	>>> from stewbeet.plugins.sniffer.model import SourceOrigin
	>>> class Fake: origin = SourceOrigin(file="/p/blocks.py", line=11, column=0)
	>>> [Mem.attribution[-1].origin.line for _ in attributed([("a", Fake())])]
	[11]
	>>> Mem.attribution
	[]
	"""
	for key, declared in definitions:
		with attribute_to(declared):
			yield key, declared

