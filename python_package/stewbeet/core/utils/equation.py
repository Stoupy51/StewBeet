
# Imports
from ..__memory__ import Mem

class ScoreboardEquation:
	def __init__(self, player: str, scoreboard: str|None = None):
		"""
		Create an equation that stores its result in a scoreboard

		Args:
			player		(str):			The player whose scoreboard will store the result. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".
		"""
		if scoreboard is None: scoreboard = f"{Mem.ctx.project_id}.data"
		self.player = player
		self.scoreboard = scoreboard
		self.text: list[str] = []
	def __str__(self) -> str:
		"""
		Returns the equation as mcfunction scoreboard operations.

		Returns:
			str: The equation as mcfunction scoreboard operations.
		"""
		return "\n".join(self.text)

	def _operation(self, player: str, scoreboard: str|None, operator: str) -> "ScoreboardEquation":
		"""
		Manipulates the scoreboard value

		Args:
			player		(str):			The player whose scoreboard value will be used in the operation. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".
			operator	(str):			The operator to use in the operation. Must be one of "*=", "/=", "+=", "-=".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		if scoreboard is None: scoreboard = f"{Mem.ctx.project_id}.data"
		self.text.append(f"scoreboard players operation {self.player} {self.scoreboard} {operator} {player} {scoreboard}")
		return self

	def multiply(self, player: str, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Multiplies the current scoreboard value

		Args:
			player		(str):			The player whose scoreboard value will be used in the multiplication. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self._operation(player, scoreboard, "*=")
	def divide(self, player: str, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Divides the current scoreboard value

		Args:
			player		(str):			The player whose scoreboard value will be used in the division. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self._operation(player, scoreboard, "/=")
	def add(self, player: str, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Adds to the current scoreboard value

		Args:
			player		(str):			The player whose scoreboard value will be used in the addition. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self._operation(player, scoreboard, "+=")
	def subtract(self, player: str, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Subtracts from the current scoreboard value

		Args:
			player		(str):			The player whose scoreboard value will be used in the subtraction. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self._operation(player, scoreboard, "-=")
	def set(self, player: str, scoreboard: str|None = None) -> "ScoreboardEquation":
		"""
		Sets the current scoreboard value

		Args:
			player		(str):			The player whose scoreboard value will be used in the set operation. Can be a selector, a player name, or a fake player.
			scoreboard	(str | None):	The scoreboard objective to use. Defaults to "{project_id}:data".

		Returns:
			ScoreboardEquation: The current equation instance, allowing for method chaining.
		"""
		return self._operation(player, scoreboard, "=")


