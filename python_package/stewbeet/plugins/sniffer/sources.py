""" Which files may be named as a mapping source, shared by every producer.

FR-010 is a validity condition rather than a quality target: a jump into `site-packages` is worse
than no jump, so a line with no valid project origin is emitted unmapped. Both the StewBeet
reconstruction path and the mecha AST path answer that question here, and neither owns the rule.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
import sys
from functools import cache

# Constants
LIBRARY_PACKAGES: tuple[str, ...] = ("stewbeet", "beet", "bolt", "mecha", "stouputils")
""" Packages whose source may never be a mapping target, even when installed editable inside the project. """


# Functions
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
def is_project_source(path: str, roots: tuple[str, ...]) -> bool:
	""" Whether a file may be named as a mapping source.

	A path qualifies only when it sits under one of `roots` **and** outside every installed
	library. The second condition is not implied by the first: StewBeet is frequently installed
	editable from inside the very repository being built.

	Args:
		path:  Absolute path of a source file.
		roots: Normalised absolute directories the project owns.

	Anything under site-packages is out, whatever the roots say:

	>>> is_project_source("/nowhere/site-packages/stewbeet/plugins/x.py", ("/nowhere",))
	False

	And so is the StewBeet package itself **even when it sits under the project root**, which is
	exactly what an editable install from inside the repository being built looks like. A plain
	root check passes this case and must not:

	>>> import os, stewbeet
	>>> package_dir = os.path.dirname(stewbeet.__file__)
	>>> repo_root = os.path.dirname(package_dir)
	>>> package_dir.startswith(repo_root)   # the library really is under the root
	True
	>>> roots = (os.path.normcase(repo_root),)
	>>> is_project_source(os.path.join(package_dir, "plugins", "sniffer", "sources.py"), roots)
	False
	>>> is_project_source(os.path.join(repo_root, "my_pack", "link.py"), roots)
	True
	"""
	normalized: str = os.path.normcase(os.path.abspath(path))
	if f"{os.sep}site-packages{os.sep}" in normalized:
		return False
	if any(normalized.startswith(root + os.sep) for root in library_roots()):
		return False
	return any(normalized.startswith(root + os.sep) or normalized == root for root in roots)


def reset_caches() -> None:
	""" Drop the caches whose inputs only hold still within one build.

	`library_roots` reads `sys.modules`, which grows as lazy imports resolve, so a package absent at
	the first call would otherwise never be excluded. Without any caching at all the roots are
	recomputed on every stack frame of every write, which measured +32% on a real build against
	+20% budgeted, so they are cached and cleared, not dropped.
	"""
	library_roots.cache_clear()
	is_project_source.cache_clear()

