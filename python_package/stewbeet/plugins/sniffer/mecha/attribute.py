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


def owner_of(location: SourceLocation, sources: dict[str, str], command: str, own: str | None = None, own_file: str | None = None) -> str | None:
	""" The one file a location can belong to, or None when it cannot be narrowed to one.

	Two things have to hold. The position must sit where the location says, and the file must
	actually say there what the command starts with. **Both are required**, and the second is not
	a tiebreaker: a function assembled in memory has commands whose position is valid in every
	file on the first character, so a lone candidate proves nothing on its own. Requiring the word
	costs 46 of 815 mappings on a real project and removes every wrong-file attribution, which is
	the trade FR-010 asks for.

	What the word check drops is a command mecha rewrote past recognition, such as a bolt
	expression compiled into `scoreboard players operation`. Its position is the least trustworthy
	of any, so losing it is not a loss.

	Args:
		command:  The command as mecha serialised it. Its first word is the evidence.
		own:      The text this unit's AST was parsed from, when it has one.
		own_file: Absolute path of that text on disk, or None when it was assembled in memory.

	>>> from tokenstream import SourceLocation
	>>> helper = "# helper module\\nappend function demo:shared:\\n    say from helper\\n"
	>>> main = "import demo:helper as _\\n\\nappend function demo:shared:\\n    say from main one\\n"
	>>> sources = {"helper.bolt": helper, "main.bolt": main}

	The spike's own case: the position is valid in one file only, and it says `say` there.

	>>> owner_of(SourceLocation(49, 3, 5), sources, "say from helper")
	'helper.bolt'
	>>> owner_of(SourceLocation(58, 4, 5), sources, "say from main one")
	'main.bolt'

	The first character of a file is a valid position in every file, so the word decides:

	>>> owner_of(SourceLocation(0, 1, 1), sources, "import demo:helper as _")
	'main.bolt'
	>>> owner_of(SourceLocation(0, 1, 1), sources, "say something else") is None
	True

	And a command whose word is nowhere near what the file says is unmapped, however confident
	the position looks:

	>>> owner_of(SourceLocation(49, 3, 5), sources, "scoreboard players set #x obj 1") is None
	True

	A function assembled in memory has no source file, and its positions index into the string it
	was parsed from. Passing that string as `own` is what stops its commands being read as
	positions in somebody else's file:

	>>> assembled = "say direct one\\nsay direct two\\n"
	>>> owner_of(SourceLocation(0, 1, 1), {"real.mcfunction": "say from a real file\\n"},
	...          "say direct one", own=assembled) is None
	True
	"""
	head: str = command.split(maxsplit=1)[0] if command.split() else ""

	# The text the AST was parsed from is the strongest evidence there is: an offset indexes into
	# it, so a command that fits there came from it and from nowhere else. Only when it does not
	# fit is this a command some other module contributed, which is the case worth searching for.
	if own is not None and sits_at(own, location.pos, location.lineno, location.colno) and own.startswith(head, location.pos):
		return own_file if own_file in sources else None

	owners: list[str] = [
		path for path, text in sources.items()
		if sits_at(text, location.pos, location.lineno, location.colno) and text.startswith(head, location.pos)
	]
	return owners[0] if len(owners) == 1 else None


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

