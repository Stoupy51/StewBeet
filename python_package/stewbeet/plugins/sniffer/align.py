
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Sequence
from dataclasses import replace
from difflib import SequenceMatcher

from .model import SourceOrigin, WriteChunk
from .sidecar import final_lines_of


# Functions
def flatten(chunks: Sequence[WriteChunk]) -> tuple[list[str], list[SourceOrigin | None]]:
	""" Expand recorded chunks into parallel line and origin lists.

	A chunk written from a string literal has its Nth line on the literal's Nth line, so the origin
	advances with it. An origin that is not a literal is a single point instead: a `Block(` call a
	plugin generated from, or a write whose content argument was a variable. Advancing there walks
	down the Python file line by line and lands on whatever happens to follow the call, so `exact`
	decides which of the two applies.
	"""
	lines: list[str] = []
	origins: list[SourceOrigin | None] = []
	for chunk in chunks:
		for offset, line in enumerate(chunk.lines):
			lines.append(line)
			if chunk.origin is None:
				origins.append(None)
				continue
			if not chunk.origin.exact:
				origins.append(chunk.origin)
				continue
			# Only the first line starts where the literal does; every later line starts at column 0.
			column: int = chunk.origin.column if offset == 0 else 0
			origins.append(replace(chunk.origin, line=chunk.origin.line + offset, column=column))
	return lines, origins


def align(chunks: Sequence[WriteChunk], text: str) -> dict[int, SourceOrigin]:
	""" Map each line of a function's final text back to where it was authored.

	Recorded chunks cannot be trusted positionally, because StewBeet rewrites functions after they
	are written: `auto.headers` prepends a header block to every one of them, and `auto.text_renders`
	substitutes inside lines. So the two sequences are reconciled instead of assumed to match.

	`equal` and `replace` opcodes keep their mapping, `insert` opcodes stay unmapped because those
	generated lines have no recorded counterpart, and `delete` opcodes are dropped. This is
	transformation-agnostic: a future plugin that rewrites functions needs no change here.

	The lines the two sequences share at each end are matched off before `difflib` sees anything.
	`find_longest_match` is quadratic in how often a line repeats, and a pack of near-identical commands is its worst case.
	Trimming hands it only what a rewrite actually changed, which for a function nobody rewrote but the header plugin is nothing at all.

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

	head: int = common_head(recorded, final)
	tail: int = common_tail(recorded, final, min(len(recorded), len(final)) - head)
	middle_recorded: list[str] = recorded[head:len(recorded) - tail]
	middle_final: list[str] = final[head:len(final) - tail]

	mapped: dict[int, SourceOrigin] = {}
	map_run(mapped, origins, 0, 0, head)
	map_run(mapped, origins, len(recorded) - tail, len(final) - tail, tail)
	if not middle_recorded or not middle_final:
		return mapped

	# `find_longest_match` walks every occurrence of a line each time it meets that line, so an element repeating a thousand times is quadratic, and a blank line is that element.
	# Calling blanks junk also aligns more commands, since difflib then anchors on the commands themselves instead of on whichever blank line came first.
	# autojunk stays off: it does the same to a command repeated across a long function, and those are the lines worth anchoring on.
	matcher = SequenceMatcher(is_blank, middle_recorded, middle_final, autojunk=False)
	for tag, i1, i2, j1, j2 in matcher.get_opcodes():
		if tag in ("equal", "replace"):
			map_run(mapped, origins, head + i1, head + j1, min(i2 - i1, j2 - j1))
	return mapped


def map_run(
	mapped: dict[int, SourceOrigin],
	origins: Sequence[SourceOrigin | None],
	recorded_at: int,
	final_at: int,
	count: int,
) -> None:
	""" Give `count` consecutive final lines the origins of the recorded lines they line up with.

	>>> origin = SourceOrigin(file="/p/x.py", line=4, column=0)
	>>> mapped: dict[int, SourceOrigin] = {}
	>>> map_run(mapped, [None, origin], recorded_at=0, final_at=7, count=2)
	>>> sorted(mapped)
	[8]
	"""
	for offset in range(count):
		origin: SourceOrigin | None = origins[recorded_at + offset]
		if origin is not None:
			mapped[final_at + offset] = origin


def is_blank(line: str) -> bool:
	""" Whether a line holds nothing to navigate to, so the alignment may move it freely.

	>>> is_blank(''), is_blank('   '), is_blank('say hi')
	(True, True, False)
	"""
	return not line.strip()


def common_head(a: Sequence[str], b: Sequence[str]) -> int:
	""" How many lines the two sequences open with in common.

	>>> common_head(["say a", "say b"], ["say a", "say c"])
	1
	"""
	limit: int = min(len(a), len(b))
	index: int = 0
	while index < limit and a[index] == b[index]:
		index += 1
	return index


def common_tail(a: Sequence[str], b: Sequence[str], limit: int) -> int:
	""" How many lines the two sequences end with in common, looking no further back than `limit`.

	The limit is what stops the two ends claiming the same line: whatever the head took is no
	longer the tail's to take.

	>>> common_tail(["say a", "say b"], ["say c", "say b"], limit=2)
	1
	"""
	index: int = 0
	while index < limit and a[len(a) - 1 - index] == b[len(b) - 1 - index]:
		index += 1
	return index

