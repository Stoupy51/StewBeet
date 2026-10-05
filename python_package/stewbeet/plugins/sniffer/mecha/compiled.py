""" What a compiled command says about its source beyond where it starts: where each of its nodes sits, and where vanilla syntax ends.

An editor showing a datapack parser the source needs both. The nodes are how it gives a bolt expression or a `~/child` path the value
mecha resolved it to, column for column, and the end of vanilla syntax is where the parser's opinion stops being worth showing:
a plugin can add commands to mecha's tree, and the build accepting them is the proof that they are right.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import re
from functools import cache
from itertools import islice

from mecha import AstCommand, AstNode, AstRoot, CommandSpec, CommandTree, Mecha
from tokenstream import SourceLocation

from ..model import ColumnPoint, CompiledLine
from .attribute import OnDisk

# Constants
WORD: re.Pattern[str] = re.compile(r"\s*\S+")
""" One literal of a command and the whitespace before it. """


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


def opaque_start(mc: Mecha, command: AstCommand, vanilla: frozenset[str], source: str) -> SourceLocation | None:
	""" Where the first piece of syntax the vanilla command tree does not have begins, None for a vanilla command.

	A nested block is mecha's own and its body is compiled as commands of their own, so it is not counted.
	A literal has no node to read a position from, so it is found as the word it is after the last argument placed before it.

	Args:
		vanilla: Every path of the vanilla command tree, see `vanilla_paths`.
		source:  Text the command was parsed from, which the positions index.
	"""
	parts: list[str] = command.identifier.split(":")
	known: int = next((count for count in range(len(parts), 0, -1) if ":".join(parts[:count]) in vanilla), 0)
	if known == len(parts):
		nested: AstCommand | None = next((argument for argument in command.arguments if isinstance(argument, AstCommand)), None)
		return None if nested is None else opaque_start(mc, nested, vanilla, source)

	prototype = mc.spec.prototypes[command.identifier]
	# A redirect drops the scope in front of it from the signature, so its entries are counted from the end.
	diverging: int = known - (len(parts) - len(prototype.signature))
	if diverging < 0:
		return command.location
	# Each argument node with the index of its entry in the signature.
	arguments: dict[int, AstNode] = dict(zip(prototype.arguments, command.arguments, strict=True))
	node: AstNode | None = arguments.get(diverging)
	if isinstance(node, AstRoot):
		return None
	if node is not None and node.location.lineno:
		return node.location
	return literal_start(prototype.signature, arguments, diverging, command.location, source)


def literal_start(
	signature: tuple[object, ...], arguments: dict[int, AstNode], diverging: int, start: SourceLocation, source: str,
) -> SourceLocation:
	""" Where entry `diverging` of a signature sits, counted in words from the last argument placed before it.

	Args:
		arguments: Each argument node by the index of its entry in the signature.
		start:     Where the command starts, counted from when no argument before it was placed.
	"""
	placed: list[int] = [index for index, argument in arguments.items() if index < diverging and argument.end_location.lineno]
	position: int = arguments[placed[-1]].end_location.pos if placed else start.pos
	for _ in range(sum(isinstance(entry, str) for entry in signature[(placed[-1] + 1 if placed else 0):diverging])):
		word = WORD.match(source, position)
		position = word.end() if word else position
	position += len(source[position:]) - len(source[position:].lstrip())
	return location_at(source, position)


def location_at(source: str, position: int) -> SourceLocation:
	""" The 1-based line and column of an offset, which is how mecha spells a position.

	>>> location_at("say a\\ncompute bolt", 14)
	SourceLocation(pos=14, lineno=2, colno=9)
	"""
	before: str = source[:position]
	return SourceLocation(position, before.count("\n") + 1, position - before.rfind("\n"))


@cache
def vanilla_paths(version: str) -> frozenset[str]:
	""" Every path of the vanilla command tree of a Minecraft version, spelled like mecha's command identifiers.

	Read from the tree mecha ships for that version, so a new version needs nothing here.

	>>> {"compute", "compute:bolt"} & vanilla_paths("26.3")
	{'compute'}
	"""
	spec = CommandSpec(tree=CommandTree.load_from(version=version))
	return frozenset(
		identifier.rsplit(":", depth)[0] for identifier in spec.prototypes for depth in range(identifier.count(":") + 1)
	)

