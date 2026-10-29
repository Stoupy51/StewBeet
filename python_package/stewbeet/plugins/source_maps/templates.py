""" Which string literal each line of written content comes from.

Content handed over in a variable or a sum was built from every literal that variable was assigned and grown with,
in an order and a number of times only the build knows. Each literal is kept as the lines it evaluates to,
with a gap for every interpolation, and the written lines are read back against them.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import ast
from collections.abc import Iterator, Sequence
from functools import cached_property

from stouputils.typing import is_generic_instance

from .model import Template

# Constants
type Assignment = ast.Assign | ast.AnnAssign | ast.AugAssign
""" A statement giving a name a value, or adding to the one it holds. """

type Position = tuple[int, int]
""" A template and one of its lines, or one of the reading states below. """

START: Position = (-1, 0)
""" Before the first line, where nothing precedes the first template. """

OPAQUE: Position = (-2, 0)
""" After a line no template explains, which may end with anything. """

END: Position = (-3, 0)
""" Past the last line. """

HOLE_COST: int = 1
""" Putting a line down to an interpolation, dearer than to text a literal spells so that text wins wherever it fits. """

MISS_COST: int = 3
""" Putting a line down to no literal, dearer than an interpolation so a `{commands}` line keeps the lines it expands to. """

SCOPES: tuple[type[ast.AST], ...] = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
""" Nodes with names of their own, so an assignment inside one never feeds a write outside it. """


# Classes
class LiteralIndex:
	""" The string literals written content is built from, for the writes of one parsed file. """

	def __init__(self, tree: ast.Module) -> None:
		self.tree: ast.Module = tree
		self.assignments: dict[ast.AST, dict[str, list[Assignment]]] = {}

	def templates(self, content: ast.expr | None) -> tuple[Template, ...]:
		""" The literals `content` is concatenated from, a name standing for every literal it was assigned and grown with.

		>>> index = LiteralIndex(ast.parse('x = "say a\\\\n"\\nfor _ in y:\\n\\tx += "say b\\\\n"\\nw(x + "say c")'))
		>>> [template.starts[0] for template in index.templates(index.tree.body[-1].value.args[0])]
		[(0, 4), (2, 6), (3, 6)]
		"""
		if content is None:
			return ()
		return tuple(LiteralIndex.template_of(literal) for literal in dict.fromkeys(self.literals_of(content, frozenset())))

	def literals_of(self, node: ast.expr, seen: frozenset[str]) -> list[ast.Constant | ast.JoinedStr]:
		""" The string literals a value is concatenated from, with none for an operand no literal spells out.

		Args:
			seen: Names being read already, so the `x` of `x = x + "say a"` is the value it grows rather than itself again.
		"""
		match node:
			case ast.Constant(value=str()) | ast.JoinedStr():
				return [node]
			case ast.BinOp(left=left, op=ast.Add(), right=right):
				return self.literals_of(left, seen) + self.literals_of(right, seen)
			case ast.Name(id=name) if name not in seen:
				return [literal for value in self.values_before(node) for literal in self.literals_of(value, seen | {name})]
			case _:
				return []

	def values_before(self, use: ast.Name) -> list[ast.expr]:
		""" What a name was assigned and grown with before `use`, from the last assignment certain to run before it. """
		scope: ast.AST = self.scope_of(use)
		reset: ast.stmt | None = self.reset_before(use, scope)
		since: tuple[int, int] = (0, 0) if reset is None else (reset.lineno, reset.col_offset)
		return [
			statement.value
			for statement in self.assignments_in(scope).get(use.id, [])
			if statement.value is not None and since <= (statement.lineno, statement.col_offset) < (use.lineno, use.col_offset)
		]

	def scope_of(self, node: ast.AST) -> ast.AST:
		""" The innermost function, class, lambda or module holding a node. """
		while not isinstance(node, SCOPES):
			node = self.parents[node]
		return node

	def reset_before(self, use: ast.Name, scope: ast.AST) -> ast.stmt | None:
		""" The last statement assigning the name afresh that runs before `use` whichever branches are taken, None when none does.

		It sits before `use`, or before a statement holding it, in the same block: one in a branch `use` is not in may not have run,
		which is why both values of an `if`/`else` reach a write after it.
		"""
		node: ast.AST = use
		while node is not scope:
			parent: ast.AST = self.parents[node]
			for _, block in ast.iter_fields(parent):
				if not (isinstance(node, ast.stmt) and is_generic_instance(block, list[ast.stmt]) and node in block):
					continue
				reset: ast.stmt | None = next((s for s in reversed(block[:block.index(node)]) if LiteralIndex.resets(s, use.id)), None)
				if reset is not None:
					return reset
			node = parent
		return None

	def assignments_in(self, scope: ast.AST) -> dict[str, list[Assignment]]:
		""" Every assignment and `+=` to a scope's own names, by name, in source order. """
		if scope not in self.assignments:
			found: dict[str, list[Assignment]] = {}
			for node in LiteralIndex.own_nodes(scope):
				match node:
					case (
						ast.Assign(targets=[ast.Name(id=name)]) | ast.AnnAssign(target=ast.Name(id=name))
						| ast.AugAssign(target=ast.Name(id=name), op=ast.Add())
					):
						found.setdefault(name, []).append(node)
					case _:
						pass
			for statements in found.values():
				statements.sort(key=lambda statement: (statement.lineno, statement.col_offset))
			self.assignments[scope] = found
		return self.assignments[scope]

	@cached_property
	def parents(self) -> dict[ast.AST, ast.AST]:
		""" Each node's parent, built only for a file where a write is handed a name. """
		return {child: node for node in ast.walk(self.tree) for child in ast.iter_child_nodes(node)}

	@staticmethod
	def template_of(literal: ast.Constant | ast.JoinedStr) -> Template:
		""" The lines a literal evaluates to, each with where it starts in the source.

		A line break written as an escape starts its line on the source line it was typed on, so `"say a\\nsay b"` starts both there.

		>>> LiteralIndex.template_of(ast.parse("x = f'''\\nsay {a}\\n'''").body[0].value)
		Template(lines=((), ('say ', None), ()), starts=((0, 4), (1, 0), (2, 0)))
		"""
		first: int = literal.lineno - 1
		lines: list[list[str | None]] = [[]]
		starts: list[tuple[int, int]] = [(first, literal.col_offset)]
		for part in literal.values if isinstance(literal, ast.JoinedStr) else [literal]:
			if not isinstance(part, ast.Constant):
				lines[-1].append(None)
				continue
			head, *rest = str(part.value).split("\n")
			lines[-1].append(head)
			for offset, text in enumerate(rest, start=1):
				line: int = min(part.lineno - 1 + offset, (part.end_lineno or part.lineno) - 1)
				lines.append([text])
				starts.append((line, literal.col_offset if line == first else 0))
		return Template(lines=tuple(tuple(token for token in line if token != "") for line in lines), starts=tuple(starts))

	@staticmethod
	def resets(statement: ast.stmt, name: str) -> bool:
		""" Whether a statement assigns the name a value that reads nothing it held. """
		match statement:
			case (
				ast.Assign(targets=[ast.Name(id=target)], value=value)
				| ast.AnnAssign(target=ast.Name(id=target), value=ast.expr() as value)
			) if target == name:
				return not any(isinstance(read, ast.Name) and read.id == name for read in ast.walk(value))
			case _:
				return False

	@staticmethod
	def own_nodes(scope: ast.AST) -> Iterator[ast.AST]:
		""" Every node of a scope, without stepping into a function, class or lambda it defines. """
		pending: list[ast.AST] = list(ast.iter_child_nodes(scope))
		while pending:
			node: ast.AST = pending.pop()
			if isinstance(node, SCOPES):
				continue
			yield node
			pending.extend(ast.iter_child_nodes(node))


class Reading:
	""" The cheapest reading of written lines as templates concatenated in any order, any number of times.

	Every line is read in a state: inside a template line, or where a template ends and the next one starts on the same line.
	A line costs nothing when a template spells it, HOLE_COST when an interpolation alone stands for it, and MISS_COST otherwise.
	The reading of least total cost wins.
	A line holding only an interpolation stands for any number of lines, which is how a `{commands}` block is read.
	"""

	def __init__(self, templates: Sequence[Template]) -> None:
		self.templates: Sequence[Template] = templates
		self.entered: list[int] = [index for index, template in enumerate(templates) if len(template.lines) > 1]
		""" The templates holding a line break, the only ones that end a line: any other is part of one. """

	def attribute(self, generated: Sequence[str]) -> list[tuple[int, int] | None]:
		""" The source position of each line, None for a line no template explains.

		>>> head = Template(lines=((), ("say head",), ()), starts=((1, 4), (2, 0), (3, 0)))
		>>> loop = Template(lines=(("say ", None), ()), starts=((5, 7), (5, 7)))
		>>> Reading([head, loop]).attribute(["", "say head", "say a", "say b", ""])
		[(1, 4), (2, 0), (5, 7), (5, 7), (5, 7)]
		>>> Reading([head, loop]).attribute(["", "say head", "kill @s", "say a", ""])
		[(1, 4), (2, 0), None, (5, 7), (5, 7)]
		"""
		if len(self.templates) == 1 and self.fits(generated):
			return list(self.templates[0].starts)

		trail: list[dict[Position, tuple[Position, Position | None]]] = []
		costs: dict[Position, int] = {START: 0}
		for index, text in enumerate(generated):
			costs, steps = self.advance(costs, text, last=index == len(generated) - 1)
			trail.append(steps)

		found: list[tuple[int, int] | None] = []
		state: Position = END
		for steps in reversed(trail):
			state, line = steps[state]
			found.append(None if line is None else self.templates[line[0]].starts[line[1]])
		return found[::-1]

	def advance(
		self, costs: dict[Position, int], text: str, *, last: bool
	) -> tuple[dict[Position, int], dict[Position, tuple[Position, Position | None]]]:
		""" The least cost of each state the next line can be read in, and the state and template line each was reached from. """
		reached: dict[Position, int] = {}
		steps: dict[Position, tuple[Position, Position | None]] = {}
		for state, cost in costs.items():
			for target, line, step in self.moves(state, text, last=last):
				if target not in reached or cost + step < reached[target]:
					reached[target] = cost + step
					steps[target] = (state, line)
		return reached, steps

	def fits(self, generated: Sequence[str]) -> bool:
		""" Whether the lines are the only template's own, one for one, which they are unless an interpolation held a line break. """
		lines: tuple[tuple[str | None, ...], ...] = self.templates[0].lines
		if len(generated) != len(lines):
			return False
		return all(Reading.matches(Reading.shape(tokens), text) for tokens, text in zip(lines, generated, strict=True))

	def moves(self, state: Position, text: str, *, last: bool) -> Iterator[tuple[Position, Position | None, int]]:
		""" Each state the next line can be read in, with the template line this one is put down to and what that costs. """
		index, row = state
		if index >= 0 and row < len(self.templates[index].lines) - 1:
			if not last:
				yield from self.inside(state, text)
		else:
			yield from self.between(state, text, last=last)
		yield (END if last else OPAQUE), None, MISS_COST

	def inside(self, state: Position, text: str) -> Iterator[tuple[Position, Position | None, int]]:
		""" The moves of a line read as a template line the template goes on after. """
		index, row = state
		if Reading.is_hole(self.tokens(state)):
			yield state, state, HOLE_COST
			yield (index, row + 1), state, HOLE_COST
		elif Reading.matches(self.tokens(state), text):
			yield (index, row + 1), state, 0

	def between(self, state: Position, text: str, *, last: bool) -> Iterator[tuple[Position, Position | None, int]]:
		""" The moves of a line starting with the end of a template, or with nothing known, which the next template ends. """
		tail: tuple[str | None, ...] = Reading.shape(self.tokens(state)) if state[0] >= 0 else ((None,) if state == OPAQUE else ())
		if last:
			if Reading.matches(tail, text):
				line, cost = self.owner(state, None, text)
				yield END, line, cost
			return
		if state[0] >= 0 and Reading.is_hole(self.tokens(state)):
			yield state, state, HOLE_COST
		for entered in self.entered:
			if not Reading.matches(tail + Reading.shape(self.tokens((entered, 0))), text):
				continue
			line, cost = self.owner(state, entered, text)
			yield (entered, 1), line, cost
			if Reading.is_hole(self.tokens((entered, 0))):
				yield (entered, 0), line, cost

	def owner(self, state: Position, entered: int | None, text: str) -> tuple[Position | None, int]:
		""" The template line a line two templates share is put down to, and what that costs.

		It is the one spelling something, the first line of the template starting there before the last line of the one ending there.
		When both are blank, a blank line goes to the template starting there and any other line to none.
		"""
		head: Position | None = None if entered is None else (entered, 0)
		tail: Position | None = state if state[0] >= 0 else None
		for line in (head, tail):
			if line is not None and not Reading.is_blank(self.tokens(line)):
				return line, HOLE_COST if Reading.is_hole(self.tokens(line)) else 0
		if text.strip():
			return None, MISS_COST
		return head or tail, 0

	def tokens(self, line: Position) -> tuple[str | None, ...]:
		""" The text of one template line, see `Template.lines`. """
		return self.templates[line[0]].lines[line[1]]

	@staticmethod
	def matches(tokens: tuple[str | None, ...], text: str) -> bool:
		""" Whether a line reads as template text, each interpolation standing for any run of characters.

		>>> Reading.matches(("tag @s add ", None, ".done"), "tag @s add mgs.done")
		True
		>>> Reading.matches(("tag @s add ", None, ".done"), "tag @s add mgs.done 1")
		False
		"""
		pieces: list[str] = [""]
		for token in tokens:
			if token is None:
				pieces.append("")
			else:
				pieces[-1] += token

		first, last = pieces[0], pieces[-1]
		if len(pieces) == 1:
			return text == first
		if len(text) < len(first) + len(last) or not text.startswith(first) or not text.endswith(last):
			return False

		# With nothing but runs of any length between them, the earliest place each piece fits is as good as any other.
		at: int = len(first)
		for piece in pieces[1:-1]:
			at = text.find(piece, at, len(text) - len(last))
			if at == -1:
				return False
			at += len(piece)
		return True

	@staticmethod
	def shape(tokens: tuple[str | None, ...]) -> tuple[str | None, ...]:
		""" A template line as it reads, one holding only an interpolation reading as that interpolation alone. """
		return (None,) if Reading.is_hole(tokens) else tokens

	@staticmethod
	def is_hole(tokens: tuple[str | None, ...]) -> bool:
		""" Whether a template line holds one interpolation and nothing else to read, so it stands for any number of lines. """
		return tokens.count(None) == 1 and all(token is None or not token.strip() for token in tokens)

	@staticmethod
	def is_blank(tokens: tuple[str | None, ...]) -> bool:
		""" Whether a template line spells nothing. """
		return all(token is not None and not token.strip() for token in tokens)

