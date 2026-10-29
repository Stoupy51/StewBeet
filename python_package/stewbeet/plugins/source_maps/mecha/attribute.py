""" Which file wrote a command, when the AST node only carries a position.

A `SourceLocation` has no filename, and the obvious substitute, the compilation unit's own `filename`,
names only the first module that contributed. A function assembled from two modules,
which is what every shulker component does to `PLAYER_TICK`, would send most of its lines to the wrong file.
The spike at `specs/001-stewbeet-vscode-dx/spike/bolt-attribution/` measured it.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Self

from mecha import CompilationUnit, Mecha
from tokenstream import SourceLocation

from ..sidecar import moved_column
from ..sources import is_project_source

# Constants
SIMILAR: float = 0.6
""" How alike an edited line and an original one must be, by `SequenceMatcher.ratio`, to count as the same line rewritten. """


# Classes
@dataclass(frozen=True)
class OnDisk:
	""" A source file as mecha parsed it and as it is on disk, which differ once a plugin edits a function before mecha compiles it.

	`Function.prepend` adds lines, and a versioning refactor rewrites `ns:impl/` into `ns:v1.2.3/` inside them.
	A line rewritten in place is still the line on disk it came from, with its columns moved through what both share,
	and a line the plugin added has no line on disk at all.

	>>> on_disk = OnDisk.of(parsed=["say added", "function ns:v1/a"], disk=["function ns:impl/a"])
	>>> on_disk.position(1, 12), on_disk.position(1, 16), on_disk.position(0, 0)
	((0, 12), (0, 18), None)
	"""

	parsed: list[str]
	disk: list[str]
	lines: dict[int, int] | None
	""" The disk line of each parsed line that has one, None when the two texts are the same. """

	@classmethod
	def read(cls, path: str, parsed: str) -> Self:
		""" The file at `path` against the text mecha parsed from it. """
		with open(path, encoding="utf-8") as file:
			return cls.of(parsed.splitlines(), file.read().splitlines())

	@classmethod
	def of(cls, parsed: list[str], disk: list[str]) -> Self:
		""" Two versions of a file, by line, matched once. """
		if parsed == disk:
			return cls(parsed, disk, None)
		lines: dict[int, int] = {}
		for tag, start, end, to, until in SequenceMatcher(None, parsed, disk, autojunk=False).get_opcodes():
			if tag == "equal":
				lines.update((start + offset, to + offset) for offset in range(end - start))
			elif tag == "replace":
				lines.update(paired_lines(parsed, disk, range(start, end), range(to, until)))
		return cls(parsed, disk, lines)

	def position(self, line: int, column: int) -> tuple[int, int] | None:
		""" The 0-based disk line and column of a parsed position, None when the plugin wrote it. """
		if self.lines is None:
			return line, column
		target: int | None = self.lines.get(line)
		if target is None:
			return None
		moved: int | None = moved_column(column, self.parsed[line], self.disk[target])
		return None if moved is None else (target, moved)


# Functions
def paired_lines(parsed: list[str], disk: list[str], edited: range, original: range) -> dict[int, int]:
	""" The lines of an edited run paired, in order, with the original lines they still look like.

	A run holding a line a plugin added has one line more than the original, and which one it is can only be told by looking.

	>>> paired_lines(["say added", "function ns:v1/a"], ["function ns:impl/a"], range(2), range(1))
	{1: 0}
	"""
	pairs: dict[int, int] = {}
	at, to = edited.start, original.start
	while at < edited.stop and to < original.stop:
		if SequenceMatcher(None, parsed[at], disk[to], autojunk=False).ratio() >= SIMILAR:
			pairs[at] = to
			at, to = at + 1, to + 1
		elif edited.stop - at >= original.stop - to:
			at += 1
		else:
			to += 1
	return pairs


def candidate_sources(mc: Mecha, directory: str, roots: tuple[str, ...]) -> dict[str, str]:
	""" Absolute path to source text, for every compiled file the project may be mapped onto.

	Every unit in the database is a candidate, not just the one being emitted,
	because a command's position belongs to whichever module wrote it.
	Units outside the project roots or inside an installed library are dropped here,
	so FR-010 holds for every line without a second check.

	Args:
		directory: beet's project directory, which `filename` is relative to.
		roots:     Normalised absolute directories the project owns.
	"""
	found: dict[str, str] = {}
	for unit in mc.database.values():
		path: str | None = source_file_of(unit, directory)
		if path is None or not unit.source:
			continue
		if is_project_source(path, roots):
			found[path] = unit.source
	return found


def source_file_of(unit: CompilationUnit, directory: str) -> str | None:
	""" Absolute path a compilation unit was parsed from, None when it was assembled in memory.

	Args:
		directory: beet's project directory, which `filename` is relative to.
	"""
	return os.path.abspath(os.path.join(directory, unit.filename)) if unit.filename else None


def owner_of(
	location: SourceLocation, sources: dict[str, str], command: str, own: str | None = None, own_file: str | None = None
) -> str | None:
	""" The one file a location can belong to, or None when it cannot be narrowed to one.

	The position must sit where the location says **and** the file must say there what the command starts with,
	since the first character of every file is a valid position. The word check costs 46 of 815 mappings on a real project (FR-010).

	Args:
		command:  The command as mecha serialised it. Its first word is the evidence.
		own:      The text this unit's AST was parsed from, when it has one.
		own_file: Absolute path of that text on disk, or None when it was assembled in memory.

	>>> sources = {"helper.bolt": "# helper module\\nappend function demo:shared:\\n    say from helper\\n"}
	>>> owner_of(SourceLocation(49, 3, 5), sources, "say from helper")
	'helper.bolt'
	"""
	head: str = command.split(maxsplit=1)[0] if command.split() else ""

	# The text the AST was parsed from is the strongest evidence, since an offset indexes into it.
	# Only a command that does not fit there came from some other module, which is the case worth searching for.
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
	"""
	if pos > len(source):
		return False
	before: str = source[:pos]
	return before.count("\n") + 1 == lineno and pos - before.rfind("\n") == colno


__test__: dict[str, str] = {
	"owner_of": """
	The spike's own case, where the first character of a file is valid everywhere so the word decides,
	and an assembled function passes its text as `own` so its commands are not read as positions in somebody else's file:

	>>> helper = "# helper module\\nappend function demo:shared:\\n    say from helper\\n"
	>>> main = "import demo:helper as _\\n\\nappend function demo:shared:\\n    say from main one\\n"
	>>> sources = {"helper.bolt": helper, "main.bolt": main}
	>>> owner_of(SourceLocation(49, 3, 5), sources, "say from helper")
	'helper.bolt'
	>>> owner_of(SourceLocation(58, 4, 5), sources, "say from main one")
	'main.bolt'
	>>> owner_of(SourceLocation(0, 1, 1), sources, "import demo:helper as _")
	'main.bolt'
	>>> owner_of(SourceLocation(0, 1, 1), sources, "say something else") is None
	True
	>>> owner_of(SourceLocation(49, 3, 5), sources, "scoreboard players set #x obj 1") is None
	True
	>>> assembled = "say direct one\\nsay direct two\\n"
	>>> owner_of(SourceLocation(0, 1, 1), {"real.mcfunction": "say from a real file\\n"},
	...          "say direct one", own=assembled) is None
	True
	""",
	"sits_at": """
	The spike's own numbers, where `pos=58, line=4, col=5` belongs to a five-line module and not to the three-line one the unit names:

	>>> helper = "# helper module\\nappend function demo:shared:\\n    say from helper\\n"
	>>> main = "import demo:helper as _\\n\\nappend function demo:shared:\\n    say from main one\\n    say from main two\\n"
	>>> sits_at(helper, 58, 4, 5), sits_at(main, 58, 4, 5)
	(False, True)
	""",
}

