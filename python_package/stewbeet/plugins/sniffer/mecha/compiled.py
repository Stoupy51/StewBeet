""" What a compiled command says about its source beyond where it starts: where each of its nodes sits, and where vanilla syntax ends.

An editor showing a datapack parser the source needs both. The nodes are how it gives a bolt expression or a `~/child` path the value
mecha resolved it to, column for column, and the end of vanilla syntax is where the parser's opinion stops being worth showing:
a plugin can add commands to mecha's tree, and the build accepting them is the proof that they are right.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from itertools import islice

from mecha import AstCommand, AstNode, Mecha
from tokenstream import SourceLocation

from ...spyglass.detect import opaque_start
from ..model import ColumnPoint, CompiledLine
from .attribute import OnDisk


# Functions
def compiled_line(
	mc: Mecha, command: AstCommand, serialized: str, source: str, disk: OnDisk, vanilla: frozenset[str], bolt: bool,
) -> CompiledLine:
	""" Everything an editor can learn about one compiled command, its source positions moved to the file on disk.

	Args:
		serialized: The command as mecha serialised it.
		source:     Text mecha parsed the command from.
		vanilla:    Every path of the vanilla command tree, see `vanilla_paths`.
	"""
	written: str = serialized.split("\n", 1)[0]
	points: list[ColumnPoint] = []
	for column, location in node_columns(mc, command, written):
		position: tuple[int, int] | None = disk.position(location.lineno - 1, location.colno - 1)
		if position is not None:
			points.append(ColumnPoint(column, *position))
	opaque: SourceLocation | None = opaque_start(mc, command, vanilla, source)
	return CompiledLine(
		written=written, points=tuple(points), bolt=bolt,
		opaque=None if opaque is None else disk.position(opaque.lineno - 1, opaque.colno - 1),
	)


def node_columns(mc: Mecha, command: AstCommand, written: str) -> list[tuple[int, SourceLocation]]:
	""" The column of `written` at which each node of the command starts and ends, with the source position it was parsed at.

	A node's text is looked for inside its parent's, after its previous sibling, which is the order a serialiser writes them in.
	A node mecha placed nowhere, or one that does not serialise on its own, is skipped, and its children are looked for in its parent.
	"""
	columns: list[tuple[int, SourceLocation]] = []
	# Source end of each open node, and where in `written` its next child is looked for.
	open_nodes: list[list[int]] = [[command.end_location.pos, 0]]
	for node in islice(command.walk(), 1, None):
		if not node.location.lineno or node.end_location.pos <= node.location.pos:
			continue
		while len(open_nodes) > 1 and node.location.pos >= open_nodes[-1][0]:
			open_nodes.pop()
		parent: list[int] = open_nodes[-1]
		text: str = serialized_alone(mc, node)
		found: int = written.find(text, parent[1])
		if found == -1:
			open_nodes.append([node.end_location.pos, parent[1]])
			continue
		end: int = found + len(text)
		columns += [(found, node.location), (end, node.end_location)]
		parent[1] = end
		open_nodes.append([node.end_location.pos, found])
	return columns


def serialized_alone(mc: Mecha, node: AstNode) -> str:
	""" A node serialised outside its command, or a string `str.find` never matches when mecha cannot serialise it alone. """
	try:
		return mc.serialize(node)
	except Exception:
		# A compound entry has no rule of its own, and its key and value are what is worth placing anyway.
		return "\0"

