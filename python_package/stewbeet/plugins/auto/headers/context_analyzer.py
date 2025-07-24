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

