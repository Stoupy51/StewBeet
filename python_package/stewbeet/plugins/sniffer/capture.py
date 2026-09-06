
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Callable, Iterable
from typing import Any

import stouputils as stp
from beet import Function
from beet.library.base import NamespaceContainer

from ...core.__memory__ import Mem
from .model import SourceOrigin, WriteChunk
from .origin import resolve_origin, resolve_site

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


def record_assignment(container: NamespaceContainer[Any], key: str, value: Any) -> None:
	""" Record `ctx.data.functions[path] = Function(...)`, which no other hook sees.

	beet's own way of writing a function builds the object and puts it in the pack, so there is no
	append to catch and no StewBeet helper to tag it. Tagging happens for every insertion, which is
	what makes a later `.append(...)` on the same path work; recording happens only when the caller
	is genuinely assigning, because `write_function`'s overwrite branch assigns too and records
	itself one frame further down.
	"""
	if not isinstance(value, Function) or container.namespace is None or not container.namespace.name:
		return

	path: str = f"{container.namespace.name}:{key}"
	tag(value, path)

	# An empty assignment has nothing to map, and recording it would claim the first line the
	# appends afterwards produce: `ctx.data.functions[p] = Function()` then `.append(...)` should
	# point at the append, which is where the command was actually written.
	if not value.text.strip():
		return

	origin, kind = resolve_site()
	if kind == "assign":
		record(path, value.text, "overwrite", origin)


def install() -> None:
	""" Patch beet's Function writers so every incremental write is captured.

	`Function.append` and `.prepend` are the single choke point every incremental write flows
	through, including `write_function`'s own. The deprecated `Block.on_place` was replaced by
	`.functions.place_secondary.obj.append(...)`, which never touches `write_function` at all,
	which is why the hook lives here.

	`NamespaceContainer.process` is the other one. Every way of putting a function into a pack ends
	there with both the namespace and the key in hand, so `ctx.data.functions[p] = Function(...)`,
	`ctx.data["ns"].functions[p] = ...` and `ctx.data[Function][p] = ...` are one hook rather than three.
	"""
	if ORIGINALS:
		return
	if not callable(getattr(Function, "append", None)) or not callable(getattr(Function, "prepend", None)):
		stp.warning("sniffer: beet's Function API is not what this plugin expects, source maps disabled")
		return

	ORIGINALS["append"] = Function.append
	ORIGINALS["prepend"] = Function.prepend
	ORIGINALS["process"] = NamespaceContainer.process # pyright: ignore[reportUnknownMemberType]

	def append(self: Function, other: Function | Iterable[str] | str) -> None:
		ORIGINALS["append"](self, other)
		record_from(self, other, "append")

	def prepend(self: Function, other: Function | Iterable[str] | str) -> None:
		ORIGINALS["prepend"](self, other)
		record_from(self, other, "prepend")

	def process(self: NamespaceContainer[Any], key: str, value: Any) -> Any:
		result: Any = ORIGINALS["process"](self, key, value)
		record_assignment(self, key, result)
		return result

	Function.append = append # pyright: ignore[reportAttributeAccessIssue]
	Function.prepend = prepend # pyright: ignore[reportAttributeAccessIssue]
	NamespaceContainer.process = process # pyright: ignore[reportAttributeAccessIssue]


def uninstall() -> None:
	""" Restore beet's own methods, so a watch rebuild does not stack patches. """
	if not ORIGINALS:
		return
	Function.append = ORIGINALS.pop("append") # pyright: ignore[reportAttributeAccessIssue]
	Function.prepend = ORIGINALS.pop("prepend") # pyright: ignore[reportAttributeAccessIssue]
	NamespaceContainer.process = ORIGINALS.pop("process") # pyright: ignore[reportAttributeAccessIssue]
	ORIGINALS.clear()

