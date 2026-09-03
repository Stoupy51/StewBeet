
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Callable, Iterable
from typing import Any

import stouputils as stp
from beet import Function

from ...core.__memory__ import Mem
from .model import SourceOrigin, WriteChunk
from .origin import resolve_origin

# Constants
PATH_ATTR: str = "__stewbeet_sniffer_path__"
""" Attribute StewBeet tags onto a beet Function so a patched write knows which path it feeds. """

ORIGINALS: dict[str, Callable[..., Any]] = {}
""" The unpatched beet methods, restored at teardown. """


# Functions
def tag(func: Function, path: str) -> Function:
	""" Record which resource location a Function belongs to.

	A beet Function does not know its own path, and the patched writers below only receive the
	object. Tagging is done from the two places that have both: `write_function` and `Resource.obj`.
	"""
	setattr(func, PATH_ATTR, path)
	return func


def record(path: str, content: str, mode: str, origin: SourceOrigin | None = None) -> None:
	""" Record one contribution to a function, mirroring `write_function`'s own semantics.

	Append adds a chunk, prepend inserts at the front, and a developer's overwrite clears what it replaced.
	A **library** overwrite deliberately does not clear: `auto.headers` rewrites every
	function with `overwrite=True` as a transformation rather than as a replacement, and wiping the
	author's chunks there would destroy every mapping in the pack. Alignment handles that case.
	"""
	if origin is None:
		origin = resolve_origin()
	chunks: list[WriteChunk] = Mem.source_map_chunks.setdefault(path, [])

	if mode == "overwrite":
		if origin is None:
			return
		chunks.clear()
	chunk = WriteChunk(lines=tuple(content.split("\n")), origin=origin)
	if mode == "prepend":
		chunks.insert(0, chunk)
	else:
		chunks.append(chunk)


def record_from(func: Function, other: Function | Iterable[str] | str, mode: str) -> None:
	""" Record a write made straight through a beet Function, the modern `.obj.append(...)` path. """
	path: str | None = getattr(func, PATH_ATTR, None)
	if path is None or not isinstance(other, str):
		return
	record(path, other, mode)


def install() -> None:
	""" Patch beet's Function writers so every incremental write is captured.

	`Function.append` and `.prepend` are the single choke point all of them flow through, including
	`write_function`'s own, so no capture code is needed there for those paths. The deprecated
	`Block.on_place` was replaced by `.functions.place_secondary.obj.append(...)`, which never
	touches `write_function` at all, which is why the hook lives here.
	"""
	if ORIGINALS:
		return
	if not callable(getattr(Function, "append", None)) or not callable(getattr(Function, "prepend", None)):
		stp.warning("sniffer: beet's Function API is not what this plugin expects, source maps disabled")
		return

	ORIGINALS["append"] = Function.append
	ORIGINALS["prepend"] = Function.prepend

	def append(self: Function, other: Function | Iterable[str] | str) -> None:
		ORIGINALS["append"](self, other)
		record_from(self, other, "append")

	def prepend(self: Function, other: Function | Iterable[str] | str) -> None:
		ORIGINALS["prepend"](self, other)
		record_from(self, other, "prepend")

	Function.append = append # pyright: ignore[reportAttributeAccessIssue]
	Function.prepend = prepend # pyright: ignore[reportAttributeAccessIssue]


def uninstall() -> None:
	""" Restore beet's own methods, so a watch rebuild does not stack patches. """
	if not ORIGINALS:
		return
	Function.append = ORIGINALS.pop("append") # pyright: ignore[reportAttributeAccessIssue]
	Function.prepend = ORIGINALS.pop("prepend") # pyright: ignore[reportAttributeAccessIssue]
	ORIGINALS.clear()

