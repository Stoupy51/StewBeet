""" Where a pack file came from, and what it was called before a refactor moved it.

beet drops a file's `source_path` as soon as any plugin reads its text, and mecha names a
compilation unit after that path. A build running `beet.contrib.find_replace` over the whole pack,
which is what versioning a datapack takes, leaves every unit unable to say which file it was
authored in. Noting the paths while beet still has them, and giving them back once mecha has
compiled, is what these do.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from typing import Any

from beet import Context
from beet.core.file import TextFileBase
from mecha import Mecha

from .__memory__ import Mem


# Functions
def remember_source_paths(ctx: Context) -> None:
	""" Note where every file in the pack was loaded from, while beet still says.

	A plugin running before the pack is loaded has nothing to sweep and hooks each file as it
	arrives instead, which is what `plugins.sniffer` does.
	"""
	for pack in (ctx.data, ctx.assets):
		for _, file in pack.all():
			if isinstance(file, TextFileBase):
				remember_source_path(file)


def remember_source_path(file: TextFileBase[Any]) -> None:
	""" Note where one file was loaded from, unless beet has forgotten or somebody got there first. """
	if file.source_path is not None:
		Mem.source_map_files.setdefault(file, str(file.source_path))


def restore_filenames(mc: Mecha, directory: str) -> None:
	""" Give every compilation unit back the `filename` beet stopped mecha from recording.

	The database is keyed by the objects mecha parsed, which is the one handle a rename cannot move
	and a substitution cannot change, so a unit meets its file again whatever the build did to the
	pack in between. A unit mecha assembled in memory never had a file and keeps none.

	Args:
		directory: beet's project directory, which `filename` is relative to.
	"""
	for file, unit in mc.database.items():
		loaded: str | None = Mem.source_map_files.get(file)
		if not unit.filename and loaded is not None:
			unit.filename = os.path.relpath(loaded, directory)


def origin_path(path: str) -> str:
	""" Resource location a function was first put in the pack under, before any refactor moved it.

	A versioning plugin deletes each `ns:impl/**` key and puts the very same object back under
	`ns:v1.2.3/**`, and anything filing its work by resource location loses track of it there.
	"""
	return Mem.source_map_origins.get(path, path)

