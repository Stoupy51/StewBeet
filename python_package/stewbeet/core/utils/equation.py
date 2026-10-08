
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import re
from typing import Literal

import stouputils as stp

from ..__memory__ import Mem
from .versions import minecraft_version_at_least

# Constants
MACRO_RE = re.compile(r"\$\(\w+\)")
AnyOperator = Literal["*", "/", "+", "-", "%", ""]
COMPUTE_VERSION: tuple[int, int] = (26, 3)
""" First version with `/compute` and arithmetic number providers: an equation becomes one command. """
PROVIDER_TYPES: dict[AnyOperator, str] = {"+": "add", "-": "sub", "*": "mul", "/": "floor_div", "%": "floor_mod"}
""" Context int provider per operator; floor_div and floor_mod round like `scoreboard players operation`. """

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

def score_provider(player: str, scoreboard: str) -> str | None:
	""" The number provider reading a score, None for a selector a provider cannot name.

	>>> score_provider("@s", "kills")
	'{type:"score",target:"this",score:"kills"}'
	>>> score_provider("#total", "kills")
	'{type:"score",target:{type:"fixed",name:"#total"},score:"kills"}'
	>>> score_provider("@p", "kills") is None
	True
	"""
	if player == "@s":
		target: str = '"this"'
	elif player.startswith("@") or is_macro_argument(player):
		return None
	else:
		target = f'{{type:"fixed",name:"{player}"}}'
	return f'{{type:"score",target:{target},score:"{scoreboard}"}}'

def combine_providers(operator: AnyOperator, left: str | None, right: str | None) -> str | None:
	""" The provider of `left <operator> right`, None when either side cannot be expressed.

	>>> combine_providers("+", "1", "2"), combine_providers("/", "7", "2")
	('{type:"add",inputs:[1,2]}', '{type:"floor_div",left:7,right:2}')
	"""
	if not operator:
		return right
	if left is None or right is None:
		return None
	if operator in ("+", "*"):
		return f'{{type:"{PROVIDER_TYPES[operator]}",inputs:[{left},{right}]}}'
	return f'{{type:"{PROVIDER_TYPES[operator]}",left:{left},right:{right}}}'


# Classes

class BaseEquation:
	""" Abstract base for chainable scoreboard equation builders.

	Subclasses implement ``render_header`` and may override ``__str__``.
	All methods return ``self`` to allow method chaining.
	"""

	__slots__ = ("comment_parts", "ops", "player", "provider", "scoreboard")

	def __init__(self, target_player: str, target_scoreboard: str | None = None) -> None:
		self.player: str = target_player
		self.scoreboard: str = target_scoreboard or f"{Mem.ctx.project_id}.data"
		self.ops: list[str] = []
		self.comment_parts: list[str] = [f"{target_player} {self.scoreboard}"]
		self.provider: str | None = score_provider(target_player, self.scoreboard)
		""" The running value as a number provider, None once an operand cannot be expressed as one. """

	def __str__(self) -> str:
		if not self.uses_compute():
			return "\n".join([f"# {self.render_header()}", *self.ops])
		macro: str = "$" if is_macro_argument(str(self.provider)) else ""
		command: str = f"{macro}execute store result {self.store_target()} run compute default integer {self.provider}"
		return f"# {self.render_header()}\n{command}"

	def uses_compute(self) -> bool:
		""" Whether `str()` renders one `/compute` command instead of the scoreboard operations in `ops`. """
		return self.provider is not None and minecraft_version_at_least(COMPUTE_VERSION)

	@stp.abstract
	def render_header(self) -> str:
		""" Returns the human-readable equation comment (without the leading ``"# "``). """
		raise NotImplementedError

	@stp.abstract
	def store_target(self) -> str:
		""" Where `execute store result` writes the value, ex: ``"score @s ns.data"``. """
		raise NotImplementedError

	# Operation builder
	def apply_operation(
		self,
		player: str | int | BaseEquation,
		scoreboard: str | None,
		operator: AnyOperator,
		temp: str = "temp",
	) -> BaseEquation:
		""" Appends the scoreboard commands for one arithmetic operation.

		An int constant is registered in load as a ``#<value>`` fake player, and a macro argument is stored in ``temp`` first.

		Args:
			player:     A selector, fake player, int constant, macro arg, or another equation.
			scoreboard: Source scoreboard, ignored for int/macro, ``self.scoreboard`` when None.
			operator:   One of ``*``, ``/``, ``+``, ``-``, or ``""`` (for assignment via operation).

		>>> eq = BaseEquation("@s")  # Its scoreboard defaults to {ctx.project_id}.data
		>>> eq.apply_operation("other_player", "other_scoreboard", "/").ops
		['scoreboard players operation @s your_namespace.data /= other_player other_scoreboard']
		"""
		# The operand as a number provider; the target stands for its running value, as in the scoreboard operations
		if isinstance(player, BaseEquation):
			operand: str | None = player.provider
		elif isinstance(player, int):
			operand = str(player)
		elif is_macro_argument(player):
			operand = player
		elif (player, scoreboard or self.scoreboard) == (self.player, self.scoreboard):
			operand = self.provider
		else:
			operand = score_provider(player, scoreboard or self.scoreboard)
		self.provider = combine_providers(operator, self.provider, operand)

		# Another equation as source is rendered first for its intermediate scoreboard operations,
		# then its final value is the source of the next operation
		cancel_next_comment: bool = False
		if isinstance(player, BaseEquation):
			# Render the other equation to generate its commands in self.ops
			self.ops.extend(player.ops)
			source_comment = str(player).splitlines()
			# The other equation's header, without its leading "# "
			self.comment_parts.append(f"{operator} ({source_comment[0][2:]})")
			cancel_next_comment = True  # Prevent the source to add up

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
			# e.g. "$scoreboard players set #temp your_namespace.data $(macro_arg)"
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
			player:     The value to assign. Can be an int, a macro arg, or a player/selector.
			scoreboard: Source scoreboard (ignored for int/macro).

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
			self.provider = str(player)
		elif is_macro_argument(player):
			self.ops.append(f"${get_scoreboard_set(self.player, self.scoreboard, player)}")
			self.provider = player
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
	# Same as true division, since Minecraft scoreboard operations are all integer-based
	def __floordiv__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.divide(other)
	def __mod__(self, other: str | int | BaseEquation) -> BaseEquation:
		return self.modulo(other)
	def __neg__(self) -> BaseEquation:
		return self.multiply(-1)


# Public classes (the ones that should be used in user code)
class ScoreboardEquation(BaseEquation):
	""" Equation whose result is stored directly in a scoreboard objective.

	>>> # Simple equation
	>>> str((ScoreboardEquation("@s").set(10) + 5) * (-2) / 3 % 4 - "#toto").splitlines()[0]
	'# scoreboard @s your_namespace.data = 10 + 5 * -2 / 3 % 4 - #toto'

	>>> # From 26.3 the whole chain is one /compute command of .provider, a macro line when an operand is a macro argument
	>>> durability = ScoreboardEquation("#temp_durability", "some_score").set("-$(amount)") * 1000000 / "$(max_damage)" - "#toto"
	>>> str(durability).splitlines()[1].split(" compute default integer ")[0]
	'$execute store result score #temp_durability some_score run'
	>>> (ScoreboardEquation("#x").set("$(amount)") * 1000000 / "$(max_damage)").provider
	'{type:"floor_div",left:{type:"mul",inputs:[$(amount),1000000]},right:$(max_damage)}'

	>>> # Before 26.3, or with an operand a number provider cannot name, the scoreboard operations in .ops are written instead
	>>> for op in durability.ops:
	...     print(op)
	$scoreboard players set #temp_durability some_score -$(amount)
	scoreboard players operation #temp_durability some_score *= #1000000 your_namespace.data
	$scoreboard players set #temp_divide your_namespace.data $(max_damage)
	scoreboard players operation #temp_durability some_score /= #temp_divide your_namespace.data
	scoreboard players operation #temp_durability some_score -= #toto some_score
	>>> print(str(ScoreboardEquation("@p").set(1) + "@a"))
	# scoreboard @p your_namespace.data = 1 + @a
	scoreboard players set @p your_namespace.data 1
	scoreboard players operation @p your_namespace.data += @a your_namespace.data

	>>> # Combining two Equation instances: the inner one is computed inline
	>>> eq4 = ScoreboardEquation("@s").set(10) * 5
	>>> eq5 = ScoreboardEquation("#toto", "some_score").set(20) * 2
	>>> (eq4 * eq5).provider
	'{type:"mul",inputs:[{type:"mul",inputs:[10,5]},{type:"mul",inputs:[20,2]}]}'
	"""  # stp: ignore[long-docstring]

	__slots__ = ()

	def __init__(self, player: str, scoreboard: str | None = None) -> None:
		super().__init__(player, scoreboard)

	def render_header(self) -> str:
		return f"scoreboard {self.player} {self.scoreboard} = {' '.join(self.comment_parts)}"

	def store_target(self) -> str:
		return f"score {self.player} {self.scoreboard}"


class StorageEquation(BaseEquation):
	""" Equation that computes via a temp scoreboard, then stores the result in a storage path.

	The ``scale`` factor is applied when flushing the temp scoreboard value to storage.

	>>> equation = StorageEquation("ns:storage", "result", 0.001, "double").set("-$(amount)") * 1000
	>>> print(str(equation))
	# storage ns:storage result = (-$(amount) * 1000) * 0.001000
	$execute store result storage ns:storage result double 0.001000 run compute default integer {type:"mul",inputs:[-$(amount),1000]}
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

	def store_target(self) -> str:
		return f"storage {self.storage} {self.path} {self.storage_type} {self.scale:f}"

	def __str__(self) -> str:
		if self.uses_compute():
			return super().__str__()
		# Add the final command to store the result in storage after all operations
		self.ops.append(f"execute store result {self.store_target()} run scoreboard players get #temp_result {self.scoreboard}")
		return super().__str__()


__test__: dict[str, str] = {
	"BaseEquation.apply_operation": """
	>>> eq2 = BaseEquation("@s")
	>>> for op in eq2.apply_operation("$(macro_arg)", None, "-", temp="temp_macro").ops:
	...     print(op)
	$scoreboard players set #temp_macro your_namespace.data $(macro_arg)
	scoreboard players operation @s your_namespace.data -= #temp_macro your_namespace.data
	>>> eq3 = BaseEquation("@s")
	>>> eq3.apply_operation(42, None, "+").ops
	['scoreboard players operation @s your_namespace.data += #42 your_namespace.data']
	""",
}

