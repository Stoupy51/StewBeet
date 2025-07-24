"""
Function relationship analysis for Minecraft datapack headers.

This module handles building the relationships between functions, tags,
advancements, and function calls to create the @within information.
"""

# Imports
from beet import Context

from .execution_parser import parse_execution_context_from_line
from .object import Header


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
                    function_path: str = function_path.get("id", "")
                    if function_path in self.mcfunctions:
                        self.mcfunctions[function_path].within.append(to_be_called)

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
        """ Analyze function calls within mcfunction files. """
        # For each mcfunction file, look at each line
        for path, header in self.mcfunctions.items():
            for line in header.content.split("\n"):

                # If the line calls a function
                if "function " in line:
                    # Get the called function
                    splitted: list[str] = line.split("function ", 1)[1].replace("\n", "").split(" ")
                    calling: str = splitted[0].replace('"', '').replace("'", "")

                    # Get additional text like macros, ex: function iyc:function {id:"51"}
                    more: str = ""
                    if len(splitted) > 1:
                        more = " " + " ".join(splitted[1:])  # Add Macros or schedule time

                    # Parse execution context from the line
                    line_context = parse_execution_context_from_line(line)

                    # Create the caller string with context if available
                    caller_info = path + more
                    if line_context:
                        caller_info += f" [ {line_context} ]"

                    # If the called function is registered, append the caller info
                    if calling in self.mcfunctions and caller_info not in self.mcfunctions[calling].within:
                        self.mcfunctions[calling].within.append(caller_info)

    def analyze_all_relationships(self) -> None:
        """ Analyze all function relationships. """
        self.analyze_function_tags()
        self.analyze_advancements()
        self.analyze_function_calls()
