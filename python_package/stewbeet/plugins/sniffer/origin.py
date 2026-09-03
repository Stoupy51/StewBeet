
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

from ...core.__memory__ import Mem
from .model import SourceOrigin

# Constants
CONTENT_PARAMETER: str = "content"
""" The name every StewBeet write helper gives its mcfunction body, and all `write_helpers` looks for. """

WRITE_METHODS: frozenset[str] = frozenset({"append", "prepend"})
""" Methods on a beet Function that author content, reached through `Resource.obj`. """

LIBRARY_PACKAGES: tuple[str, ...] = ("stewbeet", "beet", "bolt", "mecha", "stouputils")
""" Packages whose source may never be a mapping target, even when installed editable inside the project. """


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
def library_roots() -> tuple[str, ...]:
	""" Directories of the installed packages that must never be mapping targets.

	Resolved from the imported modules rather than guessed, so an editable install inside the
	project being built is still excluded.
	"""
	roots: list[str] = []
	for name in LIBRARY_PACKAGES:
		module = sys.modules.get(name)
		path: str | None = getattr(module, "__file__", None) if module else None
		if path:
			roots.append(os.path.normcase(os.path.dirname(os.path.abspath(path))))
	return tuple(roots)

@cache
def project_roots() -> tuple[str, ...]:
	""" Roots under which a file counts as the project's own source, defaulting to beet's project directory. """
	configured: list[str] = Mem.ctx.meta.get("stewbeet", {}).get("sniffer", {}).get("roots", [])
	if configured:
		return tuple(os.path.normcase(os.path.abspath(str(root))) for root in configured)
	return (os.path.normcase(os.path.abspath(str(Mem.ctx.directory))),)

@cache
def is_project_source(path: str) -> bool:
	""" Whether a file may be named as a mapping source.

	A path qualifies only when it sits under a project root **and** outside every installed
	library. The second condition is not implied by the first: StewBeet is frequently installed
	editable from inside the very repository being built.

	Args:
		path (str): Absolute path of a Python file.
	Returns:
		bool: True when the file is the project's own source.
	Examples:
		Anything under site-packages is out, whatever the roots say:

		>>> is_project_source("/nowhere/site-packages/stewbeet/plugins/x.py")
		False

		And so is the StewBeet package itself **even when it sits under the project root**, which is
		exactly what an editable install from inside the repository being built looks like. A plain
		project-root check passes this case and must not:

		>>> import os, stewbeet
		>>> package_dir = os.path.dirname(stewbeet.__file__)
		>>> repo_root = os.path.dirname(package_dir)
		>>> package_dir.startswith(repo_root)   # the library really is under the root
		True
		>>> Mem.ctx.meta.setdefault("stewbeet", {})["sniffer"] = {"roots": [repo_root]}
		>>> is_project_source(os.path.join(package_dir, "plugins", "sniffer", "origin.py"))
		False
		>>> is_project_source(os.path.join(repo_root, "my_pack", "link.py"))
		True
		>>> del Mem.ctx.meta["stewbeet"]["sniffer"]
	"""
	normalized: str = os.path.normcase(os.path.abspath(path))
	if f"{os.sep}site-packages{os.sep}" in normalized:
		return False
	if any(normalized.startswith(root + os.sep) for root in library_roots()):
		return False
	return any(normalized.startswith(root + os.sep) or normalized == root for root in project_roots())


def reset_caches() -> None:
	""" Drop the caches whose inputs only hold still within one build.

	`project_roots` reads `Mem.ctx`, which is a different project on the next build, and
	`is_project_source` is built on top of it. `library_roots` reads `sys.modules`, which grows as
	lazy imports resolve, so a package absent at the first call would otherwise never be excluded.
	Without any caching at all the roots are recomputed on every stack frame of every write, which
	measured +32% on a real build against +20% budgeted, so they are cached and cleared, not dropped.
	"""
	library_roots.cache_clear()
	project_roots.cache_clear()
	is_project_source.cache_clear()


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
		if is_project_source(filename):
			call: WriteCall | None = write_calls_of(filename).get(frame.f_lineno)
			if call is not None:
				return SourceOrigin(file=os.path.abspath(filename), line=call.line, column=call.column, exact=call.exact)
		frame = frame.f_back

	if Mem.attribution:
		return Mem.attribution[-1].origin
	return None

