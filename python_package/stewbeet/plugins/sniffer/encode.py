
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

	The sign travels in the least significant bit, the remaining bits are the magnitude, and each group carries a continuation bit.

	Args:
		value: The delta to encode.
	Returns:
		str: One or more base64 characters.

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
	""" Build the base64 VLQ `mappings` string for one generated file.

	A line opens at its column 0 and its points follow.
	Every field but the generated column runs on from the previous segment **in the file**.
	A generated line with no origin emits an empty group, and trailing unmapped lines emit no group at all.

	Args:
		mappings: Resolved lines, strictly increasing.

	>>> build_mappings([LineMapping(0, 0, 0, 0), LineMapping(2, 0, 1, 0)], generated_lines=3)
	'AAAA;;AACA'
	>>> from stewbeet.plugins.sniffer.model import ColumnPoint
	>>> build_mappings([LineMapping(0, 0, 4, 2, points=(ColumnPoint(9, 4, 13),))], generated_lines=1)
	'AAIE,SAAW'
	"""
	by_line: dict[int, LineMapping] = {row.generated_line: row for row in mappings}
	if not by_line:
		return ""

	previous_source: int = 0
	previous_source_line: int = 0
	previous_source_column: int = 0

	groups: list[str] = []
	for line in range(min(max(by_line) + 1, generated_lines)):
		row: LineMapping | None = by_line.get(line)
		if row is None:
			groups.append("")
			continue
		previous_column: int = 0
		segments: list[str] = []
		for column, source_line, source_column in [(0, row.source_line, row.source_column)] + [
			(point.generated, point.line, point.column) for point in row.points if point.generated > 0
		]:
			segments.append(
				vlq_encode(column - previous_column)
				+ vlq_encode(row.source_index - previous_source)
				+ vlq_encode(source_line - previous_source_line)
				+ vlq_encode(source_column - previous_source_column)
			)
			previous_column = column
			previous_source = row.source_index
			previous_source_line = source_line
			previous_source_column = source_column
		groups.append(",".join(segments))
	return ";".join(groups)


def to_json(source_map: FunctionSourceMap, generated_lines: int) -> JsonDict:
	""" Serialise a source map to the Source Map v3 JSON shape.

	`sourcesContent` is omitted entirely: it is optional in the standard, consumers read sources from disk through `sourceRoot`,
	and inlining would duplicate the whole project into the build.
	What only an editor needs travels in `x_` fields, which the standard leaves to vendors and every other consumer ignores.
	"""
	extensions: JsonDict = {}
	if source_map.bolt_sources:
		extensions["x_stewbeet_bolt"] = list(source_map.bolt_sources)
	if source_map.opaque:
		extensions["x_stewbeet_opaque"] = [list(position) for position in source_map.opaque]
	return {
		"version": 3,
		"file": source_map.file,
		"sourceRoot": source_map.source_root,
		"sources": list(source_map.sources),
		"names": [],
		"mappings": build_mappings(source_map.mappings, generated_lines),
		**extensions,
	}


__test__: dict[str, str] = {
	"build_mappings": """
	Conformance against the reference implementation's `hit.mcfunction`, whose five commands come from
	`source/combat/hit.ts` lines 6, 7, 8, 8 and 9, with a trailing sourceMappingURL comment that maps nowhere:

	>>> rows = [LineMapping(0, 0, 5, 0), LineMapping(1, 0, 6, 0), LineMapping(2, 0, 7, 0),
	...         LineMapping(3, 0, 7, 0), LineMapping(4, 0, 8, 0)]
	>>> build_mappings(rows, generated_lines=6)
	'AAKA;AACA;AACA;AAAA;AACA'

	And `aura.mcfunction`, from two sources: its second segment moves to the next source and three lines back in one step.

	>>> rows = [LineMapping(0, 0, 8, 0), LineMapping(1, 1, 5, 0), LineMapping(2, 1, 6, 0)]
	>>> build_mappings(rows, generated_lines=4)
	'AAQA;ACHA;AACA'
	""",
}

