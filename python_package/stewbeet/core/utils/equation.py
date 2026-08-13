
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import re
from typing import Literal

import stouputils as stp

from ..__memory__ import Mem

# Constants
MACRO_RE = re.compile(r"\$\(\w+\)")
AnyOperator = Literal["*", "/", "+", "-", "%", ""]

# Helpers
def is_macro_argument(value: str) -> bool:
	""" Returns True if the value contains a macro argument pattern like ``$(foo)``.

	>>> is_macro_argument("$(amount)")
	True
	>>> is_macro_argument("#toto")
	False
	"""
	return bool(MACRO_RE.search(value))

def get_scoreboard_set(player: str, scoreboard: str, value: str | int) -> str:
	""" Returns a ``scoreboard players set`` command string.

	>>> get_scoreboard_set("#42", "your_namespace.data", 42)
	'scoreboard players set #42 your_namespace.data 42'
	"""
	return f"scoreboard players set {player} {scoreboard} {value}"

def get_scoreboard_operation(player: str, scoreboard: str, operator: AnyOperator, source: str, source_scoreboard: str) -> str:
	""" Returns a ``scoreboard players operation`` command string.

	>>> get_scoreboard_operation("@s", "your_namespace.data", "*", "#1000000", "your_namespace.data")
	'scoreboard players operation @s your_namespace.data *= #1000000 your_namespace.data'
	"""
	return f"scoreboard players operation {player} {scoreboard} {operator}= {source} {source_scoreboard}"

def get_comment_token(operator: AnyOperator, player: str | int, scoreboard: str | None) -> str:
	""" Builds one token for the equation head comment.

	>>> get_comment_token("*", "@s", "some_score")
	'* @s some_score'
	>>> get_comment_token("+", "$(macro_arg)", None)
	'+ $(macro_arg)'
	>>> get_comment_token("", "#source", None)
	'#source'
	"""
	parts: list[str] = []
	if operator:
		parts.append(operator)
	parts.append(str(player))
	if scoreboard is not None:
		parts.append(scoreboard)
	return " ".join(parts)


# Classes

class BaseEquation:
	""" Abstract base for chainable scoreboard equation builders.

	Subclasses implement ``render_header`` and may override ``__str__``.
	All methods return ``self`` to allow method chaining.
	"""

	__slots__ = ("comment_parts", "ops", "player", "scoreboard")

	def __init__(self, target_player: str, target_scoreboard: str | None = None) -> None:
		self.player: str = target_player
		self.scoreboard: str = target_scoreboard or f"{Mem.ctx.project_id}.data"
		self.ops: list[str] = []
		self.comment_parts: list[str] = [f"{target_player} {self.scoreboard}"]

	def __str__(self) -> str:
		lines = [f"# {self.render_header()}", *self.ops]
		return "\n".join(lines)

	@stp.abstract
	def render_header(self) -> str:
		""" Returns the human-readable equation comment (without the leading ``"# "``). """
		...

	# Operation builder
	def apply_operation(
		self,
		player: str | int | BaseEquation,
		scoreboard: str | None,
		operator: AnyOperator,
		temp: str = "temp",
	) -> BaseEquation:
		""" Appends the scoreboard commands for one arithmetic operation.

		Handles three cases:
		- integer constant  -> registers it in load, uses ``#<value>`` fake player
		- macro argument    -> stores macro value in a temp variable first
		- player/selector   -> direct scoreboard operation

		Args:
			player      (str | int | BaseEquation):   Source value (selector, fake player, int constant, macro arg, or another equation).
			scoreboard  (str | None):  Source scoreboard. Ignored for int/macro; defaults to ``self.scoreboard``.
			operator    (AnyOperator): One of ``*``, ``/``, ``+``, ``-``, or ``""`` (for assignment via operation).
			temp        (str):         Name of the temporary fake player used for macro args.

		Examples:
			>>> # The following examples do not precise the scoreboard argument, so it defaults to {ctx.project_id}.data
			>>> eq = BaseEquation("@s")
			>>> eq.apply_operation("other_player", "other_scoreboard", "/").ops
			['scoreboard players operation @s your_namespace.data /= other_player other_scoreboard']

			>>> eq2 = BaseEquation("@s")
			>>> eq2.apply_operation("$(macro_arg)", None, "-", temp="temp_macro").ops
			['$scoreboard players set #temp_macro your_namespace.data $(macro_arg)', 'scoreboard players operation @s your_namespace.data -= #temp_macro your_namespace.data']

			>>> eq3 = BaseEquation("@s")
			>>> eq3.apply_operation(42, None, "+").ops
			['scoreboard players operation @s your_namespace.data += #42 your_namespace.data']
		"""
		# Special case with another equation as source:
		# we need to render it first to generate the intermediate scoreboard operations,
		# then we can use its final value as source for the next operation
		cancel_next_comment: bool = False
		if isinstance(player, BaseEquation):
			# Render the other equation to generate its commands in self.ops
			self.ops.extend(player.ops)
			source_comment = str(player).splitlines()
			self.comment_parts.append(f"{operator} ({source_comment[0][2:]})")	# Add the other equation header (without the leading "# ")
			cancel_next_comment = True	# Prevent the source to add up

			# The final value of the source equation is always stored in self.player and self.scoreboard of the source equation
			scoreboard = player.scoreboard
			player = player.player

		# Update the equation comment
		if not cancel_next_comment:
			self.comment_parts.append(get_comment_token(operator, player, scoreboard))
		add_op = self.ops.append

		# Handle different source types
		if isinstance(player, int):
			# e.g. "scoreboard players operation @s your_namespace.data += #42 your_namespace.data"
			add_op(get_scoreboard_operation(self.player, self.scoreboard, operator, f"#{player}", f"{Mem.ctx.project_id}.data"))
		elif is_macro_argument(player):
			# e.g. "$scoreboard players set #temp your_namespace.data $(macro_arg)""
			add_op(f"${get_scoreboard_set(f'#{temp}', f"{Mem.ctx.project_id}.data", player)}")
			# e.g. "scoreboard players operation @s your_namespace.data -= #temp your_namespace.data"
			add_op(get_scoreboard_operation(self.player, self.scoreboard, operator, f"#{temp}", f"{Mem.ctx.project_id}.data"))
		else:
			# e.g. "scoreboard players operation @s your_namespace.data /= other_player other_scoreboard"
			resolved: str = scoreboard or self.scoreboard
			add_op(get_scoreboard_operation(self.player, self.scoreboard, operator, str(player), resolved))

		return self

	# Public methods for operations
	def set(self, player: str | int, scoreboard: str | None = None) -> BaseEquation:
		""" Sets the scoreboard value (assignment, not operation), should be used for the first operation in the chain.

		Args:
			player      (str | int):   The value to assign. Can be an int, a macro arg, or a player/selector.
			scoreboard  (str | None):  Source scoreboard (ignored for int/macro).

		Examples:
			>>> # Setting @s in your_namespace.data to 42 and checking the generated commands with .ops
			>>> BaseEquation("@s").set(42).ops
			['scoreboard players set @s your_namespace.data 42']

			>>> # Setting @s in your_namespace.data to a macro argument and checking the generated commands with .ops
			>>> BaseEquation("@s").set("$(macro_value)").ops
			['$scoreboard players set @s your_namespace.data $(macro_value)']
		"""
		# Handle different source types for the initial set operation
		if isinstance(player, int):
			self.ops.append(get_scoreboard_set(self.player, self.scoreboard, player))
		elif is_macro_argument(player):
			self.ops.append(f"${get_scoreboard_set(self.player, self.scoreboard, player)}")
		else:
			self.apply_operation(player, scoreboard or self.scoreboard, "")

		# Reset the comment parts to only include the initial value
		self.comment_parts = [str(player) if scoreboard is None else f"{player} {scoreboard}"]
		return self

	def multiply(self, player: str | int | BaseEquation, scoreboard: str | None = None) -> BaseEquation:
		""" Multiplies the current scoreboard value. See ``apply_operation`` for details. """
		return self.apply_operation(player, scoreboard, "*", temp="temp_multiply")

	def divide(self, player: str | int | BaseEquation, scoreboard: str | None = None) -> BaseEquation:
		""" Divides the current scoreboard value. See ``apply_operation`` for details ."""
		return self.apply_operation(player, scoreboard, "/", temp="temp_divide")

	def add(self, player: str | int | BaseEquation, scoreboard: str | None = None) -> BaseEquation:
		""" Adds to the current scoreboard value. See ``apply_operation`` for details. """
		return self.apply_operation(player, scoreboard, "+", temp="temp_add")

	def subtract(self, player: str | int | BaseEquation, scoreboard: str | None = None) -> BaseEquation:
		""" Subtracts from the current scoreboard value. See ``apply_operation`` for details. """
		return self.apply_operation(player, scoreboard, "-", temp="temp_subtract")

	def modulo(self, player: str | int | BaseEquation, scoreboard: str | None = None) -> BaseEquation:
		""" Applies modulo to the current scoreboard value. See ``apply_operation`` for details. """
		return self.apply_operation(player, scoreboard, "%", temp="temp_modulo")

	# Normal Python operations
	def __add__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.add(other)
	def __sub__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.subtract(other)
	def __mul__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.multiply(other)
	def __truediv__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.divide(other)
	def __floordiv__(self, other: str | int | BaseEquation) -> BaseEquation: # Same as true div since Minecraft scoreboard operations are all integer-based
		return self.divide(other)
	def __mod__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.modulo(other)
	def __neg__(self) -> BaseEquation:
		return self.multiply(-1)


# Public classes (the ones that should be used in user code)
class ScoreboardEquation(BaseEquation):
	""" Equation whose result is stored directly in a scoreboard objective.

	Examples:
		>>> # Simple equation
		>>> str((ScoreboardEquation("@s").set(10) + 5) * (-2) / 3 % 4 - "#toto").splitlines()[0]
		'# scoreboard @s your_namespace.data = 10 + 5 * -2 / 3 % 4 - #toto'

		>>> # Building a complex equation with method chaining and checking the generated commands with .ops
		>>> result = str(ScoreboardEquation("#temp_durability", "some_score").set("-$(amount)").multiply(1000000).divide("$(max_damage)").subtract("#toto"))
		>>> shorter = str(ScoreboardEquation("#temp_durability", "some_score").set("-$(amount)") * 1000000 / "$(max_damage)" - "#toto")
		>>> expected = (
		...     "# scoreboard #temp_durability some_score = -$(amount) * 1000000 / $(max_damage) - #toto\\n"
		...     "$scoreboard players set #temp_durability some_score -$(amount)\\n"
		...     "scoreboard players operation #temp_durability some_score *= #1000000 your_namespace.data\\n"
		...     "$scoreboard players set #temp_divide your_namespace.data $(max_damage)\\n"
		...     "scoreboard players operation #temp_durability some_score /= #temp_divide your_namespace.data\\n"
		...     "scoreboard players operation #temp_durability some_score -= #toto some_score"	# <== Note that #toto inherits the scoreboard from the equation ("some_score")
		... )
		>>> result == expected and shorter == expected
		True

		>>> # Combining two Equation instances
		>>> eq4 = ScoreboardEquation("@s").set(10) * 5
		>>> eq5 = ScoreboardEquation("#toto", "some_score").set(20) * 2
		>>> result = str(eq4 * eq5)
		>>> expected = (
		...     "# scoreboard @s your_namespace.data = 10 * 5 * (scoreboard #toto some_score = 20 * 2)\\n"
		...     "scoreboard players set @s your_namespace.data 10\\n"
		...     "scoreboard players operation @s your_namespace.data *= #5 your_namespace.data\\n"
		...     "scoreboard players set #toto some_score 20\\n"
		...     "scoreboard players operation #toto some_score *= #2 your_namespace.data\\n"
		...     "scoreboard players operation @s your_namespace.data *= #toto some_score"
		... )
		>>> result == expected
		True
	"""

	__slots__ = ()

	def __init__(self, player: str, scoreboard: str | None = None) -> None:
		super().__init__(player, scoreboard)

	def render_header(self) -> str:
		return f"scoreboard {self.player} {self.scoreboard} = {' '.join(self.comment_parts)}"


class StorageEquation(BaseEquation):
	""" Equation that computes via a temp scoreboard, then stores the result in a storage path.

	The ``scale`` factor is applied when flushing the temp scoreboard value to storage.

	Examples:
		>>> start = lambda: StorageEquation("some_namespace:some_path", "result_path", 0.000005, "double").set("-$(amount)")
		>>> result = str(start().multiply(1000000).divide("$(max_damage)").subtract("#toto"))
		>>> shorter = str(start() * 1000000 / "$(max_damage)" - "#toto")
		>>> expected = (
		...     "# storage some_namespace:some_path result_path = (-$(amount) * 1000000 / $(max_damage) - #toto) * 0.000005\\n"
		...     "$scoreboard players set #temp_result your_namespace.data -$(amount)\\n"
		...     "scoreboard players operation #temp_result your_namespace.data *= #1000000 your_namespace.data\\n"
		...     "$scoreboard players set #temp_divide your_namespace.data $(max_damage)\\n"
		...     "scoreboard players operation #temp_result your_namespace.data /= #temp_divide your_namespace.data\\n"
		...     "scoreboard players operation #temp_result your_namespace.data -= #toto your_namespace.data\\n"
		...     "execute store result storage some_namespace:some_path result_path double 0.000005 run scoreboard players get #temp_result your_namespace.data"
		... )
		>>> result == expected and shorter == expected
		True
	"""

	__slots__ = ("path", "scale", "storage", "storage_type")

	def __init__(self, storage: str, path: str, scale: float = 1.0, storage_type: str = "double") -> None:
		super().__init__("#temp_result")
		self.storage: str = storage
		self.path: str = path
		self.scale: float = scale
		self.storage_type: str = storage_type
		self.comment_parts: list[str] = [f"{storage} {path}"]

	def render_header(self) -> str:
		return f"storage {self.storage} {self.path} = ({' '.join(self.comment_parts)}) * {self.scale:f}"

	def __str__(self) -> str:
		# Add the final command to store the result in storage after all operations
		self.ops.append(
			f"execute store result storage {self.storage} {self.path} {self.storage_type} {self.scale:f}"
			f" run scoreboard players get #temp_result {f"{Mem.ctx.project_id}.data"}"
		)
		return super().__str__()

