
# Imports
import os
from pathlib import Path

import stouputils as stp

from ...core import Mem

# Sub-folders of the beet project directory searched for project images
SEARCHED_FOLDERS: tuple[str, ...] = ("src", "assets")


# Utility functions
def find_project_png(filename: str, root: str | None = None) -> str | None:
	""" Find a project image in ``<root>/src/``, then ``<root>/assets/``, then any ``<root>/*<filename>``.

	Args:
		filename	(str):			Name of the image to look for, e.g. ``"pack.png"``.
		root		(str | None):	Base directory to search in, defaults to the beet project directory.
	Returns:
		str | None: Path to the image, or None when it was not found.
	"""
	if root is None:
		root = stp.clean_path(str(Mem.ctx.directory))
	for folder in SEARCHED_FOLDERS:
		path: str = f"{root}/{folder}/{filename}"
		if os.path.exists(path):
			return path
	return next((stp.clean_path(str(p)) for p in Path(root).glob(f"*{filename}")), None)


def find_pack_png(root: str | None = None) -> str | None:
	""" Find the project ``pack.png`` (the logo), or None when the project has none. """
	return find_project_png("pack.png", root)


def find_tooltip_png(root: str | None = None) -> str | None:
	""" Find a project ``tooltip.png`` replacing the packaged atlas, or None to use the packaged one. """
	return find_project_png("tooltip.png", root)

