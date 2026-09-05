""" Which file wrote a command, when the AST node only carries a position.

A `SourceLocation` has no filename, and the obvious substitute, the compilation unit's own
`filename`, names only the first module that contributed. A function assembled from two modules,
which is what every shulker component does to `PLAYER_TICK`, would send most of its lines to the
wrong file. The spike at `specs/001-stewbeet-vscode-dx/spike/bolt-attribution/` measured it.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os

from mecha import Mecha
from tokenstream import SourceLocation

from ..sources import is_project_source


# Functions
def candidate_sources(mc: Mecha, directory: str, roots: tuple[str, ...]) -> dict[str, str]:
	""" Absolute path to source text, for every compiled file the project may be mapped onto.

	Every unit in the database is a candidate, not just the one being emitted, because a command's
	position belongs to whichever module wrote it. Units outside the project roots or inside an
	installed library are dropped here, so FR-010 holds for every line without a second check.

	Args:
		directory: beet's project directory, which `filename` is relative to.
		roots:     Normalised absolute directories the project owns.
	"""
	found: dict[str, str] = {}
	for unit in mc.database.values():
		if not unit.filename or not unit.source:
			continue
		path: str = os.path.abspath(os.path.join(directory, unit.filename))
		if is_project_source(path, roots):
			found[path] = unit.source
	return found


def owner_of(location: SourceLocation, sources: dict[str, str], command: str) -> str | None:
	""" The one file a location can belong to, or None when it cannot be narrowed to one.

	Zero candidates means the writer is a library or lives outside the project. Several means the
	sources agree on all three fields, which every file does at the very first character, so the
	command's own first word breaks the tie. It only breaks ties: a position deep in a file is
	already unambiguous, and mecha rewrites enough that a command's first word often differs from
	the source that produced it.

	Still ambiguous means unmapped, because FR-010 is a validity condition: a confident jump to the
	wrong file is worse than no jump.

	Args:
		command: The command as mecha serialised it, used only to choose between candidates.
	"""
	owners: list[str] = [path for path, text in sources.items() if sits_at(text, location.pos, location.lineno, location.colno)]
	if len(owners) < 2:
		return owners[0] if owners else None

	head: str = command.split(maxsplit=1)[0] if command.split() else ""
	narrowed: list[str] = [path for path in owners if sources[path].startswith(head, location.pos)]
	return narrowed[0] if len(narrowed) == 1 else None


def sits_at(source: str, pos: int, lineno: int, colno: int) -> bool:
	""" Whether offset `pos` of `source` is at 1-based line `lineno`, column `colno`.

	The three fields of a `SourceLocation` are mutually redundant, so a file that did not produce
	the node has to agree on the offset **and** the line **and** the column to be a false positive.
	That redundancy is the whole attribution mechanism.

	>>> sits_at("ab\\ncd\\n", 3, 2, 1)
	True
	>>> sits_at("ab\\ncd\\n", 3, 1, 4)
	False

	The spike's own numbers, where `pos=58, line=4, col=5` belongs to a five-line module and not to
	the three-line one the compilation unit names:

	>>> helper = "# helper module\\nappend function demo:shared:\\n    say from helper\\n"
	>>> main = "import demo:helper as _\\n\\nappend function demo:shared:\\n    say from main one\\n    say from main two\\n"
	>>> sits_at(helper, 58, 4, 5), sits_at(main, 58, 4, 5)
	(False, True)
	"""
	if pos > len(source):
		return False
	before: str = source[:pos]
	return before.count("\n") + 1 == lineno and pos - before.rfind("\n") == colno

