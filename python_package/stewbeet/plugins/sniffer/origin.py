
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import ast
import inspect
import os
import sys
from dataclasses import dataclass
from functools import cache
from types import FrameType

from ...core.__memory__ import Mem
from .model import SourceOrigin
from .sources import is_project_source, reset_caches as reset_source_caches

# Constants
CONTENT_PARAMETER: str = "content"
""" The name every StewBeet write helper gives its mcfunction body, and all `write_helpers` looks for. """

WRITE_METHODS: frozenset[str] = frozenset({"append", "prepend"})
""" Methods on a beet Function that author content, reached through `Resource.obj`. """

GENERATED_INIT: str = "<string>"
""" Filename of the `__init__` a dataclass generates, the one frame between a definition and its declaration. """


# Classes
@dataclass(slots=True)
class WriteCall:
	""" A write call found in a source file, and where its content argument starts. """
	line: int
	column: int
	exact: bool


# Functions
@cache
def write_helpers() -> dict[str, int]:
	""" StewBeet's write helpers, mapped to the position of their content argument.

	Read off the signatures in `core.utils.io.functions` rather than listed here, so adding a helper
	there is enough for the sniffer to record it. The convention it reads is the parameter name:
	`write_function(path, content, ...)` gives 1 and `write_load_file(content, ...)` gives 0, while
	`write_tag`, having no content argument, is not a write helper at all.

	>>> write_helpers()["write_function"], write_helpers()["write_load_file"]
	(1, 0)
	>>> "write_tag" in write_helpers(), "read_function" in write_helpers()
	(False, False)
	"""
	from ...core.utils.io import functions

	found: dict[str, int] = {}
	for name, helper in inspect.getmembers(functions, inspect.isfunction):
		if helper.__module__ != functions.__name__:
			continue
		parameters: list[str] = list(inspect.signature(helper).parameters)
		if CONTENT_PARAMETER in parameters:
			found[name] = parameters.index(CONTENT_PARAMETER)
	return found


@cache
def project_roots() -> tuple[str, ...]:
	""" Roots under which a file counts as the project's own source, defaulting to beet's project directory. """
	configured: list[str] = Mem.ctx.meta.get("stewbeet", {}).get("sniffer", {}).get("roots", [])
	if configured:
		return tuple(os.path.normcase(os.path.abspath(str(root))) for root in configured)
	return (os.path.normcase(os.path.abspath(str(Mem.ctx.directory))),)


def reset_caches() -> None:
	""" Drop the caches whose inputs only hold still within one build.

	`project_roots` reads `Mem.ctx`, which is a different project on the next build, and the shared
	source filter is built on top of it.
	"""
	project_roots.cache_clear()
	reset_source_caches()


def index_write_calls(path: str) -> dict[int, WriteCall]:
	""" Map every line of a source file that holds a write call to that call's content position.

	Being inside project code is not evidence of authorship; being at a write call is.
	That is what stops a plugin-generated write from attributing to the project's entry point,
	which passes the project-source filter while having authored nothing.
	"""
	try:
		with open(path, encoding="utf-8") as file:
			tree: ast.Module = ast.parse(file.read(), filename=path)
	except (OSError, SyntaxError):
		return {}

	helpers: dict[str, int] = write_helpers()
	found: dict[int, WriteCall] = {}
	for node in ast.walk(tree):
		if not isinstance(node, ast.Call):
			continue

		content: ast.expr | None = None
		if isinstance(node.func, ast.Name) and (index := helpers.get(node.func.id)) is not None:
			content = node.args[index] if len(node.args) > index else None
			if content is None:
				content = next((kw.value for kw in node.keywords if kw.arg == CONTENT_PARAMETER), None)
		elif isinstance(node.func, ast.Attribute) and node.func.attr in WRITE_METHODS:
			content = node.args[0] if node.args else None
		else:
			continue

		# A literal argument gives the string's own position; anything else falls back to the call.
		exact: bool = isinstance(content, ast.Constant | ast.JoinedStr)
		anchor: ast.expr | ast.Call = content if (content is not None and exact) else node
		call = WriteCall(line=anchor.lineno - 1, column=anchor.col_offset, exact=exact)
		for line in range(node.lineno, (node.end_lineno or node.lineno) + 1):
			found.setdefault(line, call)
	return found

AST_CACHE: dict[str, tuple[float, dict[int, WriteCall]]] = {}
""" Parsed write-call index per file, keyed by path and validated against mtime. """

def write_calls_of(path: str) -> dict[int, WriteCall]:
	""" Cached `index_write_calls`, invalidated when the file's mtime changes. """
	try:
		mtime: float = os.path.getmtime(path)
	except OSError:
		return {}
	cached: tuple[float, dict[int, WriteCall]] | None = AST_CACHE.get(path)
	if cached is not None and cached[0] == mtime:
		return cached[1]
	calls: dict[int, WriteCall] = index_write_calls(path)
	AST_CACHE[path] = (mtime, calls)
	return calls




def declaration_origin() -> SourceOrigin | None:
	""" Where a definition was declared, or None when a library declared it.

	Called from `Item.__post_init__`, so the frames above are the construction's own: `item.py`,
	`block.py` for a `Block`, and the `__init__` the dataclass generated. Unlike `resolve_origin`
	this consults no AST index, because a constructor's caller **is** the declaration site, with no
	plugin in between to be mistaken for it.

	The case that must not be attributed is a StewBeet plugin building an `Item` itself: the walk
	stops at the first frame that is not the construction's, so it lands on the plugin and returns
	None rather than continuing out to the user's entry point, which declared nothing.

	>>> declaration_origin() is None   # a doctest frame is nobody's declaration
	True
	"""
	frame: FrameType | None = sys._getframe(1) # pyright: ignore[reportPrivateUsage]
	while frame is not None and is_constructor_frame(frame):
		frame = frame.f_back

	if frame is None or not is_project_source(frame.f_code.co_filename, project_roots()):
		return None
	line, column = call_position(frame)
	return SourceOrigin(file=os.path.abspath(frame.f_code.co_filename), line=line, column=column, exact=False)


def is_constructor_frame(frame: FrameType) -> bool:
	""" Whether a frame belongs to a definition being built rather than to whoever asked for it. """
	filename: str = frame.f_code.co_filename
	if filename == GENERATED_INIT:
		return True
	return os.path.normcase(os.path.abspath(filename)).startswith(definition_root() + os.sep)


@cache
def definition_root() -> str:
	""" Directory holding the definition dataclasses, resolved from the module rather than spelled out. """
	from ...core.cls import item
	return os.path.normcase(os.path.dirname(os.path.abspath(item.__file__)))


def call_position(frame: FrameType) -> tuple[int, int]:
	""" Line and column of the call a frame is executing, both 0-based.

	`co_positions()` carries the exact span of every instruction since Python 3.11, so the column of
	a `Block(` call is available without parsing anything. A frame built without position tables
	yields no column, and 0 is the honest answer there.

	>>> def probe() -> tuple[int, int]:
	...     return call_position(sys._getframe())
	>>> probe()[1]
	11
	"""
	positions = list(frame.f_code.co_positions())
	index: int = frame.f_lasti // 2
	if index < len(positions):
		line, _, column, _ = positions[index]
		if line is not None:
			return line - 1, column or 0
	return frame.f_lineno - 1, 0


def resolve_origin() -> SourceOrigin | None:
	""" Where the content being written was authored, or None when nothing in the project authored it.

	Three tiers, first hit wins:

	1. The innermost stack frame that is project source **and** sits on a write call.
	2. The top of the ambient attribution stack, for content a plugin generates from a declaration.
	3. Nothing, so the lines are emitted unmapped.
	"""
	frame = sys._getframe(1) # pyright: ignore[reportPrivateUsage]
	while frame is not None:
		filename: str = frame.f_code.co_filename
		if is_project_source(filename, project_roots()):
			call: WriteCall | None = write_calls_of(filename).get(frame.f_lineno)
			if call is not None:
				return SourceOrigin(file=os.path.abspath(filename), line=call.line, column=call.column, exact=call.exact)
		frame = frame.f_back

	if Mem.attribution:
		return Mem.attribution[-1].origin
	return None

