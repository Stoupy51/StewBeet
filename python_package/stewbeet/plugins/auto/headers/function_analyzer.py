"""
Function relationship analysis for Minecraft datapack headers.

This module handles building the relationships between functions, tags,
advancements, and function calls to create the @within information.
"""

# pyright: reportUnnecessaryIsInstance=false
# Imports
import re
from typing import cast

from beet import Context

from .execution_parser import parse_execution_context_from_line
from .object import Header

FUNCTION_CALL_RE = re.compile(r"function\s+([#]?[\w./-]+:[\w./-]+)")


# Class
class FunctionAnalyzer:
    """ Analyzes function relationships and builds @within information. """

    def __init__(self, ctx: Context, mcfunctions: dict[str, Header]):
        """ Initialize the function analyzer.

        Args:
            ctx (Context): The beet context
            mcfunctions (Dict[str, Header]): Dictionary mapping function paths to Header objects
        """
        self.ctx = ctx
        self.mcfunctions = mcfunctions

    def analyze_function_tags(self) -> None:
        """ Analyze function tags and build relationships. """
        # For each function tag, get the functions that it calls
        for tag_path, tag in self.ctx.data.function_tags.items():
            # Get string that is used for calling the function (ex: "#namespace:my_function")
            to_be_called: str = f"#{tag_path}"

            # Loop through the functions in the tag
            for function_path in tag.data["values"]:
                if isinstance(function_path, str):
                    if function_path in self.mcfunctions:
                        self.mcfunctions[function_path].within.append(to_be_called)
                elif isinstance(function_path, dict):
                    function_path_str: str = cast(dict[str,str],function_path).get("id", "")
                    if function_path_str in self.mcfunctions:
                        self.mcfunctions[function_path_str].within.append(to_be_called)

    def analyze_advancements(self) -> None:
        """ Analyze advancements and build relationships. """
        # For each advancement, get the functions that it calls
        for adv_path, adv in self.ctx.data.advancements.items():
            # Get string that is used for calling the function (ex: "advancement namespace:my_function")
            to_be_called: str = f"advancement {adv_path}"

            # Check if the advancement has a function reward
            if adv.data.get("rewards", {}).get("function"):
                function_path: str = adv.data["rewards"]["function"]
                if function_path in self.mcfunctions:
                    self.mcfunctions[function_path].within.append(to_be_called)

    def analyze_function_calls(self) -> None:
        """ Analyze function calls within mcfunction files.

        Examples:
            Detecting nested function references inside macro payloads:
            >>> caller = Header(
            ...     "test:caller",
            ...     [],
            ...     [],
            ...     'function #bs.raycast:run {with: {on_exit_point: "function test:earth/on_exit"}}',
            ... )
            >>> raycast = Header("#bs.raycast:run", [], [], "")
            >>> exit_fn = Header("test:earth/on_exit", [], [], "")
            >>> mcfunctions = {
            ...     "test:caller": caller,
            ...     "#bs.raycast:run": raycast,
            ...     "test:earth/on_exit": exit_fn,
            ... }
            >>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
            >>> analyzer.analyze_function_calls()
            >>> any(item.startswith("test:caller") for item in mcfunctions["test:earth/on_exit"].within)
            True
        """
        # For each mcfunction file, look at each line
        for path, header in self.mcfunctions.items():
            for line in header.content.split("\n"):

                # If the line calls a function
                if "function " in line:
                    # Split the line on "function " to get before and after parts
                    split_on_function: list[str] = line.split("function ", 1)
                    before_function: str = split_on_function[0]
                    after_function: str = split_on_function[1].replace("\n", "")

                    # Get the called function
                    splitted: list[str] = after_function.split(" ")
                    calling: str = splitted[0].replace('"', '').replace("'", "")
                    called_functions: list[str] = [calling]

                    # Also detect nested function references in arguments, e.g.
                    # function #tag:run {with: {on_exit_point: "function namespace:path"}}
                    for match in FUNCTION_CALL_RE.finditer(line):
                        candidate = match.group(1)
                        if candidate not in called_functions:
                            called_functions.append(candidate)

                    # Get additional text like macros, ex: function iyc:function {id:"51"}
                    more: str = ""
                    if len(splitted) > 1:
                        more = " " + " ".join(splitted[1:])  # Add Macros or schedule time

                    # Check if "schedule" appears right before "function" (loses execution context)
                    is_scheduled: bool = before_function.rstrip().endswith("schedule")

                    # Parse execution context from the line (only if not scheduled)
                    line_context: str | None = None
                    if not is_scheduled:
                        line_context = parse_execution_context_from_line(line)

                    # Create the caller string with context if available
                    caller_info: str = path + more
                    if line_context:
                        line_context = "".join(
                            x for i, x in enumerate(line_context)
                            if x != " " or (i > 0 and line_context[i - 1] not in ":,")
                        )
                        caller_info += f" [ {line_context} ]"
                    elif is_scheduled:
                        # Mark scheduled calls with a special marker so context analyzer knows not to inherit context
                        caller_info += " [ scheduled ]"

                    # If a called function is registered, append the caller info
                    for called in called_functions:
                        if called in self.mcfunctions and caller_info not in self.mcfunctions[called].within:
                            self.mcfunctions[called].within.append(caller_info)

    def analyze_all_relationships(self) -> None:
        """ Analyze all function relationships. """
        self.analyze_function_tags()
        self.analyze_advancements()
        self.analyze_function_calls()
