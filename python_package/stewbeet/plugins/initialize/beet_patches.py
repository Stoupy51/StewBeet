""" Monkey patches applied to beet at the very start of every build.

These live here instead of in a beet fork so upstream stays pullable. Each patch keeps the exact
behaviour of what it replaces and is applied once per process, never re-wrapping on the second build
of a `stewbeet watch` session.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from collections.abc import Iterator
from pathlib import Path

import beet.library.utils
import stouputils as stp
from beet import Pack
from beet.core.utils import FileSystemPath

# Variables
patches_applied: bool = False
""" Whether `apply_beet_patches` already ran in this process. """


# Functions
def fast_list_files(directory: FileSystemPath) -> Iterator[Path]:
	""" Drop-in replacement for `beet.library.utils.list_files`, without the `Path.relative_to` cost.

	Upstream builds a `Path` out of every walked file and then re-parses it through
	`relative_to(directory)`, which is about five times slower than slicing the prefix off the string
	`os.walk` already hands over.

	Args:
		directory (FileSystemPath): The directory to walk.
	Returns:
		Iterator[Path]: Every file below the directory, as a path relative to it.

	Examples:
		>>> import tempfile
		>>> with tempfile.TemporaryDirectory() as tmp:
		...     Path(tmp, "sub").mkdir()
		...     _ = Path(tmp, "sub", "a.txt").write_text("a")
		...     sorted(path.as_posix() for path in fast_list_files(tmp))
		['sub/a.txt']
	"""
	base: str = os.fspath(directory)
	prefix_length: int = len(base) + (0 if base.endswith(("/", os.sep)) else 1)
	for root, _, files in os.walk(base):
		relative_root: str = root[prefix_length:]
		for filename in files:
			yield Path(relative_root, filename)


def apply_beet_patches() -> None:
	""" Install every beet monkey patch, once per process. """
	global patches_applied
	if patches_applied:
		return
	patches_applied = True

	# Rebind the module global: `list_origin` is beet's only caller and resolves it at call time
	beet.library.utils.list_files = fast_list_files

	# Retry saving when another program (vscode, Minecraft, ...) holds a file locked for a moment
	Pack.save = stp.retry(Pack.save, exceptions=PermissionError, max_attempts=10, delay=1.0, backoff=2.0)  # type: ignore

