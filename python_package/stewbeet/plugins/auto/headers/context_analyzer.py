"""
Context analysis utilities for determining execution contexts of Minecraft functions.

This module handles analyzing function call relationships and determining
the execution context based on caller information.
"""

# Imports
from .object import Header


# Class
class ContextAnalyzer:
    """ Analyzes and determines execution contexts for Minecraft functions. """

    def __init__(self, mcfunctions: dict[str, Header]):
        """ Initialize the context analyzer.

        Args:
            mcfunctions (dict[str, Header]): dictionary mapping function paths to Header objects
        """
        self.mcfunctions = mcfunctions
        self.execution_contexts: dict[str, str | None] = {}

    def determine_execution_context(self, func_path: str, visited: set[str] | None = None) -> str | None:
        """ Determine the execution context of a function based on its callers.

        Args:
            func_path (str): The path of the function to analyze
            visited (set[str] | None): Set of already visited functions to prevent infinite recursion

        Returns:
            str | None: The execution context, or None if unknown

        Examples:
            Function called by an advancement returns player context:
            >>> h = Header("test:func", ["advancement test:my_advancement"], [], "say hi")
            >>> ctx_analyzer = ContextAnalyzer({"test:func": h})
            >>> ctx_analyzer.determine_execution_context("test:func")
            'as the player & at current position'

            Function called by tick tag returns None:
            >>> h2 = Header("test:tick", ["#minecraft:tick"], [], "say tick")
            >>> ctx_analyzer2 = ContextAnalyzer({"test:tick": h2})
            >>> ctx_analyzer2.determine_execution_context("test:tick") is None
            True

            Function called only by scheduled callers has no context:
            >>> h3 = Header("test:sched", ["test:load [ scheduled ]"], [], "say hi")
            >>> ctx_analyzer3 = ContextAnalyzer({"test:sched": h3})
            >>> ctx_analyzer3.determine_execution_context("test:sched") is None
            True

            Function with explicit execution context in caller brackets:
            >>> h4 = Header("test:child", ["test:parent [ as @e at @s ]"], [], "say hi")
            >>> ctx_analyzer4 = ContextAnalyzer({"test:child": h4})
            >>> ctx_analyzer4.determine_execution_context("test:child").strip()
            'as @e at @s'

            Unknown function path returns None:
            >>> ctx_analyzer5 = ContextAnalyzer({})
            >>> ctx_analyzer5.determine_execution_context("nonexistent:func") is None
            True
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

            # Advancement functions are executed as the player at current position
            if caller.startswith("advancement "):
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
                    if any(keyword in context for keyword in ["as ", "at ", "positioned ", "rotated ", "facing ", "in ", "anchored ", "align "]):
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

