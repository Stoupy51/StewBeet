
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass, field


# Classes
@dataclass(frozen=True, slots=True)
class ColumnPoint:
	""" A column of a generated line that is also a position in its source, which is what each end of an AST node is. """
	generated: int
	line: int
	""" 0-based source line, which is not the command's own for an argument written on a continuation line. """
	column: int


@dataclass(frozen=True, slots=True)
class CompiledLine:
	""" What mecha knows about a command beyond where it starts. A StewBeet write has none of it. """
	written: str
	""" The command as mecha serialised it, which the columns of `points` index. """
	points: tuple[ColumnPoint, ...]
	opaque: tuple[int, int] | None
	""" 0-based source line and column where syntax no vanilla parser knows begins, None for a vanilla command. """
	bolt: bool
	""" Whether the file it was written in is bolt or mecha syntax rather than vanilla mcfunction. """


@dataclass(frozen=True, slots=True)
class SourceOrigin:
	""" Where a chunk of written content came from in the author's own Python.

	Only ever a file in the project's own source tree. A candidate that fails the project-source
	filter yields None rather than a degraded origin, because a jump into library internals is
	worse than no jump at all.

	Args:
		file:   Absolute path of the .py file holding the write call.
		line:   0-based line of the content literal, or of the call when it is not a literal.
		column: 0-based column of the same.
		exact:  False when the position is the call rather than a literal.
	"""
	file: str
	line: int
	column: int
	exact: bool = True
	compiled: CompiledLine | None = None


@dataclass(frozen=True, slots=True)
class AttributionScope:
	""" Ambient fallback used when no project frame is on the stack.

	Pushed by a plugin generating on a declaration's behalf, so the generated lines reach the
	declaration site instead of the plugin that emitted them.
	"""
	origin: SourceOrigin


@dataclass(frozen=True, slots=True)
class WriteChunk:
	""" One write call's contribution to one function, recorded in call order.

	Several chunks with different origins in one function is the normal case, not an edge case.
	"""
	lines: tuple[str, ...]
	origin: SourceOrigin | None


@dataclass(frozen=True, slots=True)
class LineMapping:
	""" One resolved generated line. Lines with no origin are absent rather than present-and-empty. """
	generated_line: int
	source_index: int
	source_line: int
	source_column: int
	points: tuple[ColumnPoint, ...] = ()
	""" Columns of the final line, past the first, that are positions in the same source. """


@dataclass(frozen=True, slots=True)
class FunctionSourceMap:
	""" The emitted artifact for one generated function.

	`sourcesContent` is deliberately absent: it is not part of the format, and inlining every
	Python source into every map would cost tens of megabytes on a real project.
	"""
	generated_path: str
	source_root: str
	sources: tuple[str, ...]
	mappings: tuple[LineMapping, ...]
	file: str = field(default="")
	bolt_sources: tuple[int, ...] = ()
	""" Indices of the `sources` written in bolt or mecha syntax, which no vanilla parser reads. """
	opaque: tuple[tuple[int, int, int], ...] = ()
	""" Source index, line and column where syntax a plugin added to mecha begins. """

