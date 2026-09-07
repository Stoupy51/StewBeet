# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import fnmatch
import os
from glob import glob

import stouputils as stp
from beet import Context
from stouputils.typing import JsonDict


# Functions
def lib_archives(ctx: Context, pack_type: str) -> list[str]:
	""" Library archives of a pack type, minus the ones filtered out by ``meta.stewbeet.libs_exclude_patterns``.

	Patterns are matched against the archive path relative to the libs folder, ex: "resource_pack/*ARAM*.zip".
	An excluded archive is invisible to every plugin: it is neither welded nor copied to a destination.

	Args:
		ctx       (Context): The beet context.
		pack_type (str):     Either "datapack" or "resource_pack".
	Returns:
		Absolute paths of the archives to ship, in glob order.
	"""
	stewbeet_config: JsonDict = ctx.meta.get("stewbeet", {})
	libs_folder: str = str(stewbeet_config.get("libs_folder", "libs"))
	if not libs_folder or not os.path.isdir(f"{libs_folder}/{pack_type}"):
		return []

	exclude_patterns: list[str] = stewbeet_config.get("libs_exclude_patterns", [])
	root: str = os.path.abspath(libs_folder)
	return [
		path for path in (os.path.abspath(x) for x in glob(f"{libs_folder}/{pack_type}/*.zip"))
		if not any(fnmatch.fnmatch(stp.relative_path(path, root), pattern) for pattern in exclude_patterns)
	]

