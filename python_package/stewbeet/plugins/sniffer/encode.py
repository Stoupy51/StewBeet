
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Iterable

from stouputils.typing import JsonDict

from .model import FunctionSourceMap, LineMapping

# Constants
BASE64: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
""" The Source Map v3 base64 alphabet, indexed by 6-bit group. """

VLQ_CONTINUATION: int = 32
""" Bit set on a group when another group follows. """


# Functions
def vlq_encode(value: int) -> str:
	""" Encode one signed integer as base64 VLQ.

	The sign travels in the least significant bit, the remaining bits are the magnitude, and each
	group carries a continuation bit.

	Args:
		value (int): The delta to encode.
	Returns:
		str: One or more base64 characters.
	Examples:
		>>> vlq = vlq_encode
		>>> vlq(0), vlq(1), vlq(-1), vlq(5), vlq(-3), vlq(8)
		('A', 'C', 'D', 'K', 'H', 'Q')
		>>> vlq_encode(16)
		'gB'
	"""
	encoded: int = (-value << 1) + 1 if value < 0 else value << 1
	out: str = ""
	while True:
		group: int = encoded & 31
		encoded >>= 5
		out += BASE64[group | VLQ_CONTINUATION] if encoded else BASE64[group]
		if not encoded:
			return out


def build_mappings(mappings: Iterable[LineMapping], generated_lines: int) -> str:
	""" Build the `mappings` string for one generated file.

	Every field is delta-encoded against the previous segment **in the file**, not within the line,
	which is the detail hand-rolled encoders get wrong. A generated line with no origin emits an
	empty group; trailing unmapped lines emit no group at all and the string simply ends.

	Args:
		mappings        (Iterable[LineMapping]): Resolved lines, strictly increasing.
		generated_lines (int):                   Total lines in the generated file.
	Returns:
		str: The base64 VLQ mappings string.
	Examples:
		Conformance against someone else's encoder. This is the line table of the reference
		implementation's `hit.mcfunction`, whose five commands come from `source/combat/hit.ts`
		lines 6, 7, 8, 8 and 9 (1-based), with a trailing sourceMappingURL comment that maps nowhere:

		>>> rows = [LineMapping(0, 0, 5, 0), LineMapping(1, 0, 6, 0), LineMapping(2, 0, 7, 0),
		...         LineMapping(3, 0, 7, 0), LineMapping(4, 0, 8, 0)]
		>>> build_mappings(rows, generated_lines=6)
		'AAKA;AACA;AACA;AAAA;AACA'

		And `aura.mcfunction`, generated from two different sources. Its second segment moves to the
		next source *and* three lines backwards in one step, because the deltas are file-wide:

		>>> rows = [LineMapping(0, 0, 8, 0), LineMapping(1, 1, 5, 0), LineMapping(2, 1, 6, 0)]
		>>> build_mappings(rows, generated_lines=4)
		'AAQA;ACHA;AACA'

		An unmapped line in the middle is an empty group, which is not the same as no group:

		>>> build_mappings([LineMapping(0, 0, 0, 0), LineMapping(2, 0, 1, 0)], generated_lines=3)
		'AAAA;;AACA'
	"""
	by_line: dict[int, LineMapping] = {row.generated_line: row for row in mappings}
	if not by_line:
		return ""

	previous_column: int = 0
	previous_source: int = 0
	previous_source_line: int = 0
	previous_source_column: int = 0

	groups: list[str] = []
	for line in range(min(max(by_line) + 1, generated_lines)):
		row: LineMapping | None = by_line.get(line)
		if row is None:
			groups.append("")
			continue
		groups.append(
			vlq_encode(0 - previous_column)
			+ vlq_encode(row.source_index - previous_source)
			+ vlq_encode(row.source_line - previous_source_line)
			+ vlq_encode(row.source_column - previous_source_column)
		)
		previous_column = 0
		previous_source = row.source_index
		previous_source_line = row.source_line
		previous_source_column = row.source_column
	return ";".join(groups)


def to_json(source_map: FunctionSourceMap, generated_lines: int) -> JsonDict:
	""" Serialise a source map to the Source Map v3 JSON shape.

	`sourcesContent` is omitted entirely: it is optional in the standard, consumers read sources
	from disk through `sourceRoot`, and inlining would duplicate the whole project into the build.
	"""
	return {
		"version": 3,
		"file": source_map.file,
		"sourceRoot": source_map.source_root,
		"sources": list(source_map.sources),
		"names": [],
		"mappings": build_mappings(source_map.mappings, generated_lines),
	}

