"""
Context analysis utilities for determining execution contexts of Minecraft functions.

This module handles analyzing function call relationships and determining
the execution context based on caller information.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from .object import Header

# Constants
PLAYER_CONTEXT: str = "as the player & at current position"
""" The context of a function an advancement reward or a dialog button runs. """

DEFAULT_CONTEXT_CALLERS: tuple[str, ...] = ("#minecraft:tick", "#minecraft:load")
""" Callers running a function with no context at all. """

EXECUTE_KEYWORDS: tuple[str, ...] = ("as ", "at ", "positioned ", "rotated ", "facing ", "in ", "anchored ", "align ")
""" What a bracketed caller suffix must hold to be an execution context rather than an NBT path. """


# Class
class ContextAnalyzer:
	""" Analyzes and determines execution contexts for Minecraft functions. """

	def __init__(self, mcfunctions: dict[str, Header]):
		""" Initialize the context analyzer.

		Args:
			mcfunctions: dictionary mapping function paths to Header objects
		"""
		self.mcfunctions = mcfunctions
		self.execution_contexts: dict[str, str | None] = {}

	def determine_execution_context(self, func_path: str, visited: set[str] | None = None) -> str | None:
		""" Execution context of a function deduced from its callers, None if unknown.

		Advancements and dialog buttons run as the player, while tick and scheduled callers carry no context.

		>>> h = Header("test:func", ["advancement test:my_advancement"], [], "say hi")
		>>> ctx_analyzer = ContextAnalyzer({"test:func": h})
		>>> ctx_analyzer.determine_execution_context("test:func")
		'as the player & at current position'
		>>> h4 = Header("test:child", ["test:parent [ as @e at @s ]"], [], "say hi")
		>>> ctx_analyzer4 = ContextAnalyzer({"test:child": h4})
		>>> ctx_analyzer4.determine_execution_context("test:child").strip()
		'as @e at @s'
		"""
		if visited is None:
			visited = set()
		if func_path in visited:
			return None
		if func_path in self.execution_contexts:
			return self.execution_contexts[func_path]
		visited.add(func_path)
		if func_path not in self.mcfunctions:
			return None
		context: str | None = self.context_from_callers(self.mcfunctions[func_path].within, visited)
		self.execution_contexts[func_path] = context
		return context

	def context_from_callers(self, within: list[str], visited: set[str]) -> str | None:
		""" The context the first caller able to tell gives, a function inheriting the context of the function calling it.

		A scheduled caller tells nothing, since the call runs on a later tick.
		"""
		for caller in within:
			if " [ scheduled ]" in caller:
				continue
			if caller.startswith(("advancement ", "dialog ")):
				return PLAYER_CONTEXT
			if caller in DEFAULT_CONTEXT_CALLERS:
				return None
			context: str | None = bracketed_context(caller)
			if context is not None:
				return context
			base_caller: str = caller.split(" ")[0]
			if base_caller in self.mcfunctions:
				return self.determine_execution_context(base_caller, visited.copy())
		return None

	def analyze_all_contexts(self) -> None:
		""" Analyze and determine execution contexts for all functions. """
		for path in self.mcfunctions:
			context = self.determine_execution_context(path)
			# Only set the context if it's not None
			if context is not None:
				self.mcfunctions[path].executed = context



def bracketed_context(caller: str) -> str | None:
	""" The execution context between ` [` and the last `]` of a caller, None when it holds none.

	>>> bracketed_context("t:f [ as @a ]"), bracketed_context("t:f {path:a[0]}")
	(' as @a ', None)
	"""
	if " [" not in caller or "]" not in caller:
		return None
	context: str = caller[caller.find(" [") + 2:caller.rfind("]")]
	return context if any(keyword in context for keyword in EXECUTE_KEYWORDS) else None


__test__: dict[str, str] = {
	"ContextAnalyzer.determine_execution_context": """
	>>> hd = Header("test:menu", ["dialog test:config"], [], "say hi")
	>>> ContextAnalyzer({"test:menu": hd}).determine_execution_context("test:menu")
	'as the player & at current position'
	>>> h2 = Header("test:tick", ["#minecraft:tick"], [], "say tick")
	>>> ctx_analyzer2 = ContextAnalyzer({"test:tick": h2})
	>>> ctx_analyzer2.determine_execution_context("test:tick") is None
	True
	>>> h3 = Header("test:sched", ["test:load [ scheduled ]"], [], "say hi")
	>>> ctx_analyzer3 = ContextAnalyzer({"test:sched": h3})
	>>> ctx_analyzer3.determine_execution_context("test:sched") is None
	True
	>>> ctx_analyzer5 = ContextAnalyzer({})
	>>> ctx_analyzer5.determine_execution_context("nonexistent:func") is None
	True
	""",
}

