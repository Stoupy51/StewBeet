""" Which of the project's own `.mcfunction` sources no vanilla parser can read.

Four things take a source file out of vanilla mcfunction, and all are read off structures the build
already has rather than guessed from the text: bolt generated Python for it, mecha split it into
more than one function, one of its commands spans several lines, or one is a command a plugin added to mecha.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
import re
from collections import Counter
from collections.abc import Callable
from functools import cache
from itertools import pairwise

from beet import Context
from bolt import Runtime
from mecha import AstCommand, AstNode, AstRoot, CommandSpec, CommandTree, CompilationUnit, Mecha, MechaOptions
from tokenstream import SourceLocation

from ...core.source_paths import restore_filenames

# Constants
WORD: re.Pattern[str] = re.compile(r"\s*\S+")
""" One literal of a command and the whitespace before it. """


# Functions
def unparseable_sources(ctx: Context) -> list[str]:
	""" Project-relative paths of the `.mcfunction` sources Spyglass reports as broken.

	Returns:
		Sorted forward-slash paths, the shape `env.exclude` patterns are matched against.
	"""
	mc: Mecha | None = existing_service(ctx, Mecha)
	if mc is None:
		return []
	restore_filenames(mc, os.path.abspath(str(ctx.directory)))
	found: set[str] = nested_sources(mc) | bolt_sources(ctx, mc) | spread_sources(mc) | opaque_sources(mc, project_vanilla_paths(ctx))
	return sorted(name for name in found if name.endswith(".mcfunction"))


def opaque_sources(mc: Mecha, vanilla: frozenset[str]) -> set[str]:
	""" Files holding a command a plugin added to mecha's tree, which the build accepts and no vanilla parser reads.

	Args:
		vanilla: Every path of the vanilla command tree, see `vanilla_paths`.
	"""
	return {
		name for unit in mc.database.values()
		if (name := project_relative(unit.filename)) is not None and unit.ast is not None and unit.source
		and any(opaque_start(mc, command, vanilla, unit.source) is not None for command in unit.ast.commands)
	}


def spread_sources(mc: Mecha) -> set[str]:
	""" Files holding a command written over several lines, which mecha's `multiline` mode and bolt's brackets allow.

	Counted as more than one line of text between where a command starts and where the next one does,
	since a plugin's node may carry no end position. A blank line, a comment and vanilla's own `\\` continuation do not count.
	"""
	found: set[str] = set()
	for unit in mc.database.values():
		name: str | None = project_relative(unit.filename)
		if name is None or unit.ast is None or not unit.source:
			continue
		lines: list[str] = unit.source.splitlines()
		starts: list[int] = [*sorted({command.location.lineno - 1 for command in unit.ast.commands}), len(lines)]
		if any(written_lines(lines[start:end]) > 1 for start, end in pairwise(starts)):
			found.add(name)
	return found


def written_lines(lines: list[str]) -> int:
	""" How many of the lines hold text, a blank line, a comment and a line a `\\` continues left aside.

	>>> written_lines(["execute", "    as @a", "", "# note", "    run say hi"]), written_lines(["say a \\\\", "  b"])
	(3, 1)
	"""
	return sum(
		bool(line.strip()) and not line.lstrip().startswith("#") and not (index > 0 and lines[index - 1].rstrip().endswith("\\"))
		for index, line in enumerate(lines)
	)


def nested_sources(mc: Mecha) -> set[str]:
	""" Files backing more than one compilation unit, which is mecha's `function ./name:` nesting.

	Nesting is not vanilla syntax twice over: the line opening a body ends in a colon, and `./name` is not a resource location.
	A file using it is a file Spyglass underlines.
	"""
	# A unit mecha nested out of a file has no file of its own, and the text its AST was parsed from
	# is the parent file's own, which is all that ties the two together.
	named: dict[str, str] = {}
	for unit in mc.database.values():
		name: str | None = project_relative(unit.filename)
		if name is not None and unit.source:
			named.setdefault(unit.source, name)

	counts: Counter[str] = Counter()
	for unit in mc.database.values():
		name = project_relative(unit.filename) or named.get(unit.source or "")
		if name is not None:
			counts[name] += 1
	return {name for name, count in counts.items() if count > 1}


def bolt_sources(ctx: Context, mc: Mecha) -> set[str]:
	""" Files bolt generated Python for, which is every file that used bolt syntax.

	A plain function compiled while bolt is loaded keeps its `python` at None, so this says the file
	used bolt rather than that bolt was available.
	"""
	runtime: Runtime | None = existing_service(ctx, Runtime)
	if runtime is None:
		return set()

	found: set[str] = set()
	for file, module in runtime.modules.registry.items():
		if not module.python:
			continue
		unit: CompilationUnit | None = mc.database.get(file)
		name: str | None = project_relative(unit.filename) if unit else None
		if name is not None:
			found.add(name)
	return found


def existing_service[T](ctx: Context, service: Callable[[Context], T]) -> T | None:
	""" A service this build already has, or None when nothing asked for one.

	`ctx.inject` creates what it cannot find, and creating bolt's runtime at the end of a build
	would enable bolt on a project that does not use it, so the container is read instead.
	"""
	if not any(key is service for key in ctx._container): # pyright: ignore[reportPrivateUsage]
		return None
	return ctx.inject(service)


def project_relative(filename: str | None) -> str | None:
	""" A compiled file's path relative to the project root, or None when no pattern could name it.

	`CompilationUnit.filename` is already relative to beet's project directory,
	so this normalises separators and drops what an `env.exclude` entry cannot reach:
	Spyglass matches its patterns against paths relative to the root it indexes.

	>>> project_relative("src/data/ns/function/a.mcfunction")
	'src/data/ns/function/a.mcfunction'
	>>> project_relative("src\\\\data\\\\ns\\\\function\\\\a.mcfunction")
	'src/data/ns/function/a.mcfunction'
	>>> [project_relative(outside) for outside in ("../shared/x.mcfunction", "/tmp/x.mcfunction", "D:/x.mcfunction", None)]
	[None, None, None, None]
	"""
	if not filename:
		return None
	name: str = filename.replace("\\", "/")
	return None if name.startswith(("../", "/")) or ":" in name else name


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


def project_vanilla_paths(ctx: Context) -> frozenset[str]:
	""" The vanilla command paths of the Minecraft version the project compiles for. """
	return vanilla_paths(str(ctx.validate("mecha", MechaOptions).version or ctx.minecraft_version))


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

