
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Sequence
from dataclasses import replace
from difflib import SequenceMatcher

from .model import SourceOrigin, WriteChunk


# Functions
def flatten(chunks: Sequence[WriteChunk]) -> tuple[list[str], list[SourceOrigin | None]]:
	""" Expand recorded chunks into parallel line and origin lists.

	A chunk's Nth line came from the Nth line of its string literal, so the origin advances with it.
	"""
	lines: list[str] = []
	origins: list[SourceOrigin | None] = []
	for chunk in chunks:
		for offset, line in enumerate(chunk.lines):
			lines.append(line)
			if chunk.origin is None:
				origins.append(None)
				continue
			# Only the first line starts where the literal does; every later line starts at column 0.
			column: int = chunk.origin.column if offset == 0 else 0
			origins.append(replace(chunk.origin, line=chunk.origin.line + offset, column=column))
	return lines, origins


def final_lines_of(text: str) -> list[str]:
	""" Split a function's final text the way a consumer counts its lines, without the phantom trailing entry. """
	lines: list[str] = text.split("\n")
	if lines and lines[-1] == "":
		lines.pop()
	return lines


def align(chunks: Sequence[WriteChunk], text: str) -> dict[int, SourceOrigin]:
	""" Map each line of a function's final text back to where it was authored.

	Recorded chunks cannot be trusted positionally, because StewBeet rewrites functions after they
	are written: `auto.headers` prepends a header block to every one of them, and `auto.text_renders`
	substitutes inside lines. So the two sequences are reconciled instead of assumed to match.

	`equal` and `replace` opcodes keep their mapping, `insert` opcodes stay unmapped because those
	generated lines have no recorded counterpart, and `delete` opcodes are dropped. This is
	transformation-agnostic: a future plugin that rewrites functions needs no change here.

	Args:
		chunks (Sequence[WriteChunk]): Recorded contributions, in write order.
		text   (str):                  The function's final text.
	Returns:
		dict[int, SourceOrigin]: Generated line index to origin, for mapped lines only.
	Examples:
		A header prepended after the fact leaves its own lines unmapped and shifts the rest:

		>>> origin = SourceOrigin(file="/p/x.py", line=10, column=0)
		>>> chunks = [WriteChunk(lines=("say a", "say b"), origin=origin)]
		>>> mapped = align(chunks, "#> ns:demo\\nsay a\\nsay b\\n")
		>>> sorted(mapped), [mapped[k].line for k in sorted(mapped)]
		([1, 2], [10, 11])

		A line rewritten in place keeps its mapping, because difflib reports it as `replace`:

		>>> mapped = align(chunks, "say a\\nsay B RENDERED\\n")
		>>> sorted(mapped), [mapped[k].line for k in sorted(mapped)]
		([0, 1], [10, 11])
	"""
	recorded, origins = flatten(chunks)
	final: list[str] = final_lines_of(text)
	if not recorded or not final:
		return {}

	# autojunk would treat common lines as noise on any function over 200 lines, which mcfunction
	# hits easily through repeated blanks and identical commands, and would wreck the alignment.
	matcher = SequenceMatcher(None, recorded, final, autojunk=False)

	mapped: dict[int, SourceOrigin] = {}
	for tag, i1, i2, j1, j2 in matcher.get_opcodes():
		if tag not in ("equal", "replace"):
			continue
		for offset in range(min(i2 - i1, j2 - j1)):
			origin: SourceOrigin | None = origins[i1 + offset]
			if origin is not None:
				mapped[j1 + offset] = origin
	return mapped

