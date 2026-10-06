""" Scanning and rewriting text components inside already-generated files.

By the time the finalization plugins run, every text component has been serialised into the text of a datapack file:
a ``tellraw`` argument, a loot table entry, a dialog body. Those files are not plain JSON (bolt and mecha emit single-quoted
strings and unquoted keys), so the passes that need to rewrite them work on fragments of text rather than on parsed objects.

Both :mod:`stewbeet.plugins.auto.lang_file` and :mod:`stewbeet.plugins.auto.text_renders` do the same three things,
which is what this module factors out: iterate the datapack's text files, skip the ones that cannot possibly match,
and splice a list of replacements back in one pass.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Iterator
from typing import NamedTuple

from beet import Context, TextFileBase

from ...__memory__ import Mem

# Constants
CLOSERS: dict[str, str] = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
""" Closing character of each opening one, used when walking a fragment of serialized text. """


# Classes
class Replacement(NamedTuple):
	""" A slice of a file's text to overwrite.

	>>> Replacement(start=1, end=5, fragment='"x"')
	Replacement(start=1, end=5, fragment='"x"')
	"""
	start: int
	""" Index of the first character to replace. """
	end: int
	""" Index just past the last character to replace. """
	fragment: str
	""" Text to splice in place of ``string[start:end]``. """


# Functions
def find_enclosing_object(string: str, match_start: int, match_end: int) -> tuple[int, int] | None:
	""" Slice bounds of the JSON object enclosing a match, None when there is none.

	Walks backwards from match_start to the opening '{', then forwards to its matching '}', nested braces included.

	Args:
		match_end: Unused, kept for API consistency.

	>>> find_enclosing_object('{"color":"red","text":"hi"}', 16, 25)
	(0, 27)
	>>> find_enclosing_object('{"outer":{"text":"inner"}}', 10, 24)
	(9, 25)
	"""
	obj_start: int | None = opening_brace(string, match_start)
	if obj_start is None:
		return None
	obj_end: int | None = closing_brace(string, obj_start)
	return None if obj_end is None else (obj_start, obj_end)


def opening_brace(string: str, start: int) -> int | None:
	""" Index of the '{' enclosing `start`, walking backwards over the objects closed before it. """
	depth: int = 0
	for i in range(start, -1, -1):
		if string[i] == '}':
			depth += 1
		elif string[i] == '{':
			if depth == 0:
				return i
			depth -= 1
	return None


def closing_brace(string: str, opening: int) -> int | None:
	""" Index just past the '}' matching the '{' at `opening`. """
	depth: int = 0
	for i in range(opening, len(string)):
		depth += {"{": 1, "}": -1}.get(string[i], 0)
		if string[i] == '}' and depth == 0:
			return i + 1
	return None


def apply_replacements(string: str, replacements: list[Replacement]) -> str:
	""" Splice every replacement into ``string`` in a single pass.

	Replacements may come in any order and must not overlap; they are sorted here and applied from
	the end so earlier indices stay valid.

	Returns:
		The rewritten text, the input itself when there is nothing to do.

	>>> apply_replacements('{"a":1,"b":2}', [Replacement(1, 6, '"x":9')])
	'{"x":9,"b":2}'
	>>> apply_replacements('abcdef', [Replacement(4, 6, 'Z'), Replacement(0, 2, 'Y')])
	'YcdZ'
	>>> apply_replacements('unchanged', [])
	'unchanged'
	"""
	if not replacements:
		return string
	pieces: list[str] = []
	cursor: int = 0
	for start, end, fragment in sorted(replacements):
		pieces.append(string[cursor:start])
		pieces.append(fragment)
		cursor = end
	pieces.append(string[cursor:])
	return "".join(pieces)


def iter_data_text_files(ctx: Context | None = None) -> Iterator[TextFileBase[str]]:
	""" Yield every text file of the datapack, loot tables first.

	Loot tables are pulled in explicitly: they are not always reached through ``ctx.data.all()``
	depending on how they were registered.

	Args:
		ctx: The beet context (None falls back to :attr:`Mem.ctx`).
	Yields:
		TextFileBase[str]: Each text file, in a stable order so builds stay reproducible.
	"""
	if ctx is None:
		ctx = Mem.ctx
	files: dict[str, TextFileBase[str] | None] = {}
	files.update(ctx.data.loot_tables)  # type: ignore[arg-type]
	files.update(dict(ctx.data.all()))  # type: ignore[arg-type]
	for _, content in sorted(files.items()):
		if isinstance(content, TextFileBase):
			yield content


__test__: dict[str, str] = {
	"find_enclosing_object": """
	>>> find_enclosing_object('{"text":"hello"}', 1, 15)
	(0, 16)
	>>> find_enclosing_object('no braces here', 0, 5) is None
	True
	>>> find_enclosing_object('[{"text":"a"},{"text":"b"}]', 2, 12)
	(1, 13)
	>>> find_enclosing_object('[{"text":"a"},{"text":"b"}]', 15, 25)
	(14, 26)
	""",
}

