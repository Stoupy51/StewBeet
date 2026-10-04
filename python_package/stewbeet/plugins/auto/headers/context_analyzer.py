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

		within = self.mcfunctions[func_path].within

		# If no callers, default context
		if not within:
			self.execution_contexts[func_path] = None
			return self.execution_contexts[func_path]

		# Check for specific contexts
		for caller in within:

			# Scheduled functions have no execution context - skip them
			if " [ scheduled ]" in caller:
				continue

			# Advancement rewards and dialog buttons both run as the clicking/earning player
			if caller.startswith(("advancement ", "dialog ")):
				self.execution_contexts[func_path] = "as the player & at current position"
				return self.execution_contexts[func_path]

			# Tick and load tags have default context
			if caller in ["#minecraft:tick", "#minecraft:load"]:
				self.execution_contexts[func_path] = None
				return self.execution_contexts[func_path]

			# Check if caller has execution context in brackets
			if " [" in caller and "]" in caller:
				# Extract the execution context (must have space before [ to distinguish from NBT paths)
				context_start = caller.find(" [")
				context_end = caller.rfind("]")  # Find the LAST ] not the first
				if context_start != -1 and context_end != -1:
					context = caller[context_start + 2:context_end]  # +2 to skip " ["
					# Only consider it an execution context if it contains execution keywords
					if any(
						keyword in context
						for keyword in ["as ", "at ", "positioned ", "rotated ", "facing ", "in ", "anchored ", "align "]
					):
						self.execution_contexts[func_path] = context
						return self.execution_contexts[func_path]

			# If called by another function, inherit its context
			# Extract the function name (remove macros and context info)
			base_caller = caller.split(" ")[0]  # Get just the function path
			if base_caller in self.mcfunctions:
				parent_context = self.determine_execution_context(base_caller, visited.copy())
				self.execution_contexts[func_path] = parent_context
				return self.execution_contexts[func_path]

		# Default context
		self.execution_contexts[func_path] = None
		return self.execution_contexts[func_path]

	def analyze_all_contexts(self) -> None:
		""" Analyze and determine execution contexts for all functions. """
		for path in self.mcfunctions:
			context = self.determine_execution_context(path)
			# Only set the context if it's not None
			if context is not None:
				self.mcfunctions[path].executed = context


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

