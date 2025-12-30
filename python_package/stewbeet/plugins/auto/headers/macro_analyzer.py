"""
Macro analysis utilities for automatically detecting and typing macro arguments.

This module combines macro variable extraction and type inference to automatically
populate the @args section in function headers.
"""

# Imports
import stouputils as stp

from .macro_parser import is_macro_function
from .object import Header
from .type_inference import infer_macro_types


# Class
class MacroAnalyzer:
    """ Analyzes macro functions and infers argument types.

    Examples:
        Basic usage with simple macro:
        >>> target = Header("test:target", ["test:caller {x:10,y:20}"], [], "$tp @s $(x) $(y) 0")
        >>> analyzer = MacroAnalyzer({"test:target": target})
        >>> analyzer.analyze_macro_arguments("test:target")
        >>> target.args
        {'x': ('int', []), 'y': ('int', [])}

        With storage call (like StardustFragment):
        >>> caller_content = 'data modify storage test:temp macro set value {dimension:"minecraft:overworld",x:0,y:64,z:0}\\nfunction test:teleport with storage test:temp macro'
        >>> caller = Header("test:caller", [], [], caller_content)
        >>> target = Header("test:teleport", ["test:caller with storage test:temp macro"], [], "$execute in $(dimension) run tp @s $(x) $(y) $(z)")
        >>> analyzer = MacroAnalyzer({"test:caller": caller, "test:teleport": target})
        >>> analyzer.analyze_macro_arguments("test:teleport")
        >>> target.args['dimension']
        ('string', [])
        >>> target.args['x']
        ('int', [])

        Preserving manual descriptions:
        >>> target = Header("test:func", ["test:caller {value:100}"], [], "$say $(value)")
        >>> target.args = {'value': ('int', ['manually added description'])}
        >>> analyzer = MacroAnalyzer({"test:func": target})
        >>> analyzer.analyze_macro_arguments("test:func")
        >>> target.args['value']
        ('int', ['manually added description'])
    """

    def __init__(self, mcfunctions: dict[str, Header]):
        """ Initialize the macro analyzer.

        Args:
            mcfunctions (dict[str, Header]): Dictionary mapping function paths to Header objects
        """
        self.mcfunctions = mcfunctions
        self.analyzing: set[str] = set()  # Track functions currently being analyzed to prevent infinite recursion

    def analyze_macro_arguments(self, func_path: str) -> None:
        """ Analyze a single function's macro arguments and update its header.

        Recursively analyzes caller functions to ensure their types are available.

        Args:
            func_path (str): The path of the function to analyze
        """
        if func_path not in self.mcfunctions:
            return

        header = self.mcfunctions[func_path]

        # Check if it's a macro function
        if not is_macro_function(header.content):
            return

        # Prevent infinite recursion
        if func_path in self.analyzing:
            return

        self.analyzing.add(func_path)

        # Save existing manually-written args to preserve them (with their descriptions)
        existing_args: dict[str, tuple[str, list[str]]] = dict(header.args) if header.args else {}

        # First, recursively analyze all caller functions
        for caller in header.within:
            # Extract the caller function path (everything before the first space or {)
            import re
            caller_match: re.Match[str] | None = re.match(r'([^\s{]+)', caller)
            if caller_match:
                caller_func: str = caller_match.group(1)
                # Recursively analyze the caller to ensure its types are populated
                self.analyze_macro_arguments(caller_func)

        # Now infer types for this function (callers should have their types by now)
        inferred_types: dict[str, str] = infer_macro_types(header, self.mcfunctions)

        # Check if there are missing parameters (existed in inferred but not in manual args)
        missing_params: list[str] = []
        if existing_args:  # Only check if there were already args defined
            for arg_name in inferred_types:
                if arg_name not in existing_args:
                    missing_params.append(arg_name)

        # Merge: start with inferred types (without descriptions), then override with any existing manual types (with descriptions)
        # This preserves manual annotations (including descriptions) while filling in missing ones
        merged_args: dict[str, tuple[str, list[str]]] = {}

        # First, add all inferred types (without descriptions since they're auto-generated)
        for arg_name, arg_type in inferred_types.items():
            merged_args[arg_name] = (arg_type, [])

        # Then, override with any manually specified types (manual takes precedence, keeps descriptions)
        for arg_name, (arg_type, description_lines) in existing_args.items():
            merged_args[arg_name] = (arg_type, description_lines)

        # Update the header's args with merged result
        header.args = merged_args

        # Warn if there were missing parameters
        if missing_params:
            stp.warning(f"Function '{func_path}' had incomplete @args: missing {', '.join(missing_params)}")

        self.analyzing.remove(func_path)

    def analyze_all_macros(self) -> None:
        """ Analyze all macro functions and infer their argument types.

        Uses recursive analysis to handle any depth of function call chains.
        """
        for func_path in self.mcfunctions:
            self.analyze_macro_arguments(func_path)
