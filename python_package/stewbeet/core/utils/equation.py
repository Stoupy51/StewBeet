
# Imports
from ..__memory__ import Mem
from .io import read_function, write_load_file
from re import compile

macro_pattern = compile(r"\$\(\w+\)")
def _is_macro_argument(value: str):
	return macro_pattern.search(value) is not None
def _get_scoreboard_set(player: str, scoreboard: str, value: str|int) -> str:
	return f"scoreboard players set {player} {scoreboard} {value}"
def _get_scoreboard_operation(player: str, scoreboard: str, operator: str, value: str, value_scoreboard: str) -> str:
	return f"scoreboard players operation {player} {scoreboard} {operator} {value} {value_scoreboard}"
def _write_constant_to_load(value: int) -> None:
	"""
	Writes a constant definition to the load file if it doesn't already exist.

	Args:
		value (int): The constant value to write.
	"""
	load_path: str = f"{Mem.ctx.project_id}:v{Mem.ctx.project_version}/load/confirm_load"
	existing_load_content: str = read_function(load_path) if load_path in Mem.ctx.data.functions else ""
	constant_definition: str = _get_scoreboard_set(f"#{value}", f"{Mem.ctx.project_id}.data", value)
	if constant_definition not in existing_load_content.splitlines():
		write_load_file(constant_definition)

class ScoreboardEquation:
	def __init__(self, player: str, scoreboard: str|None = None):
		"""
		Create an equation that stores its result in a scoreboard

		Args:
			player		(str):			The player whose scoreboard will store the result. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".

		Examples:
			>>> from unittest.mock import MagicMock
			>>> from stewbeet.core.__memory__ import Mem
			>>> Mem.ctx = MagicMock()
			>>> Mem.ctx.project_id = "test"
			>>> Mem.ctx.project_version = "1.0.0"

			>>> str(ScoreboardEquation("#temp_durability", "some_score").set("-$(amount)").multiply(1000000).divide("$(max_damage)").subtract("#toto"))
			'$scoreboard players set #temp_durability some_score -$(amount)\\nscoreboard players operation #temp_durability some_score *= #1000000 test.data\\n$scoreboard players set #temp_divide test.data $(max_damage)\\nscoreboard players operation #temp_durability some_score /= #temp_divide test.data\\nscoreboard players operation #temp_durability some_score -= #toto test.data'
		"""
		if scoreboard is None: scoreboard = f"{Mem.ctx.project_id}.data"
		self.player = player
		self.scoreboard = scoreboard
		self.operations: list[str] = []
	def __str__(self) -> str:
		"""
		Returns the equation as mcfunction scoreboard operations.

		Returns:
			str: The equation as mcfunction scoreboard operations.
		"""
		return "\n".join(self.operations)

	def __operation(self, player: str|int, scoreboard: str|None, operator: str, temp_name: str = "temp") -> "ScoreboardEquation":
		"""
		Manipulates the scoreboard value

		Args:
			player		(str | int):	The player whose scoreboard value will be used in the operation. Can be a selector, a player name, a fake player, an integer constant, or a macro argument.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data", ignored if player is an integer constant or a macro argument.
			operator	(str):			The operator to use in the operation. Must be one of "*=", "/=", "+=", "-=".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.

		Examples:
			>>> from unittest.mock import MagicMock
			>>> from stewbeet.core.__memory__ import Mem
			>>> Mem.ctx = MagicMock()
			>>> Mem.ctx.project_id = "test"
			>>> Mem.ctx.project_version = "1.0.0"

			>>> ScoreboardEquation("@s")._ScoreboardEquation__operation("other_player", "other_scoreboard", "/=").operations
			['scoreboard players operation @s test.data /= other_player other_scoreboard']

			>>> ScoreboardEquation("@s")._ScoreboardEquation__operation("$(macro_arg)", None, "-=", "temp_macro").operations
			['$scoreboard players set #temp_macro test.data $(macro_arg)', 'scoreboard players operation @s test.data -= #temp_macro test.data']

			>>> ScoreboardEquation("@s")._ScoreboardEquation__operation(42, None, "+=").operations
			['scoreboard players operation @s test.data += #42 test.data']
		"""
		if scoreboard is None: scoreboard = f"{Mem.ctx.project_id}.data"
		if isinstance(player, int):
			_write_constant_to_load(player)
			self.operations.append(_get_scoreboard_operation(self.player, self.scoreboard, operator, f"#{player}", f"{Mem.ctx.project_id}.data"))
		elif _is_macro_argument(player):
			# store in temp variable
			self.operations.append(f"${_get_scoreboard_set(f'#{temp_name}', f'{Mem.ctx.project_id}.data', player)}")
			self.operations.append(_get_scoreboard_operation(self.player, self.scoreboard, operator, f"#{temp_name}", f"{Mem.ctx.project_id}.data"))
		else:
			self.operations.append(_get_scoreboard_operation(self.player, self.scoreboard, operator, player, scoreboard))
		return self

	def multiply(self, player: str|int, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Multiplies the current scoreboard value

		Args:
			player		(str | int):	The player whose scoreboard value will be used in the multiplication. Can be a selector, a player name, a fake player, an integer constant, or a macro argument.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data", ignored if player is an integer constant or a macro argument.

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self.__operation(player, scoreboard, "*=", temp_name="temp_multiply")
	def divide(self, player: str|int, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Divides the current scoreboard value

		Args:
			player		(str | int):	The player whose scoreboard value will be used in the division. Can be a selector, a player name, a fake player, an integer constant, or a macro argument.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data", ignored if player is an integer constant or a macro argument.

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self.__operation(player, scoreboard, "/=", temp_name="temp_divide")
	def add(self, player: str|int, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Adds to the current scoreboard value

		Args:
			player		(str | int):	The player whose scoreboard value will be used in the addition. Can be a selector, a player name, a fake player, an integer constant, or a macro argument.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data", ignored if player is an integer constant or a macro argument.

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self.__operation(player, scoreboard, "+=", temp_name="temp_add")
	def subtract(self, player: str|int, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Subtracts from the current scoreboard value

		Args:
			player		(str | int):	The player whose scoreboard value will be used in the subtraction. Can be a selector, a player name, a fake player, an integer constant, or a macro argument.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data", ignored if player is an integer constant or a macro argument.

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self.__operation(player, scoreboard, "-=", temp_name="temp_subtract")
	def set(self, player: str|int, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Sets the current scoreboard value

		Args:
			player		(str | int):	The player whose scoreboard value will be used in the setting. Can be a selector, a player name, a fake player, an integer constant, or a macro argument.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data", ignored if player is an integer constant or a macro argument.

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.

		Examples:
			>>> from unittest.mock import MagicMock
			>>> from stewbeet.core.__memory__ import Mem
			>>> Mem.ctx = MagicMock()
			>>> Mem.ctx.project_id = "test"
			>>> Mem.ctx.project_version = "1.0.0"

			>>> ScoreboardEquation("@s").set(42).operations
			['scoreboard players set @s test.data 42']

			>>> ScoreboardEquation("@s").set("$(macro_value)").operations
			['$scoreboard players set @s test.data $(macro_value)']
		"""
		if isinstance(player, int):
			# it's useless constant value in this case
			self.operations.append(_get_scoreboard_set(self.player, self.scoreboard, player))
		elif _is_macro_argument(player):
			# it's useless to use temporary variable in this case
			self.operations.append(f"${_get_scoreboard_set(self.player, self.scoreboard, player)}")
		else:
			return self.__operation(player, scoreboard, "=")
		return self

class StorageEquation(ScoreboardEquation):
	def __init__(self, storage: str, path: str, scale: float = 1.0):
		"""
		Create an equation that stores its result in a storage

		Args:
			storage	(str):	The storage to store the result in, in the format "namespace:path".
			path	(str):	The path in the storage to store the result in.
			scale	(float):	The scale to apply to the result when storing it. Defaults to 1.0.

		Examples:
			>>> from unittest.mock import MagicMock
			>>> from stewbeet.core.__memory__ import Mem
			>>> Mem.ctx = MagicMock()
			>>> Mem.ctx.project_id = "test"
			>>> Mem.ctx.project_version = "1.0.0"

			>>> str(StorageEquation("some_namespace:some_path", "result_path", 0.000005).set("-$(amount)").multiply(1000000).divide("$(max_damage)").subtract("#toto"))
			'$scoreboard players set #temp_result test.data -$(amount)\\nscoreboard players operation #temp_result test.data *= #1000000 test.data\\n$scoreboard players set #temp_divide test.data $(max_damage)\\nscoreboard players operation #temp_result test.data /= #temp_divide test.data\\nscoreboard players operation #temp_result test.data -= #toto test.data\\nexecute store result storage some_namespace:some_path result_path double 0.000005 run scoreboard players get #temp_result test.data'
		"""
		super().__init__("#temp_result")
		self.storage = storage
		self.path = path
		self.scale = scale
	def __str__(self) -> str:
		self.operations.append(f"execute store result storage {self.storage} {self.path} double {format(self.scale, 'f')} run scoreboard players get #temp_result {Mem.ctx.project_id}.data")
		return super().__str__()

# Public API
class Equation:
	scoreboard = ScoreboardEquation
	storage = StorageEquation

