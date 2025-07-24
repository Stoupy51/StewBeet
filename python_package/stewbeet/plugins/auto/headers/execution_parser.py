"""
Execution context parsing utilities for Minecraft function headers.

This module handles parsing execute commands to extract execution contexts
like 'as @e[...] & at @s' from command lines.
"""

# Imports
import re
from typing import Any

# Functions
def parse_execution_context_from_line(line: str) -> str | None:
    """ Parse execution context from a line that calls a function.
    
    Args:
        line (str): The line containing the function call
        
    Returns:
        str | None: The execution context, or None if default
    """
    line = line.strip()
    
    # If it's not an execute command, no specific context
    if not line.startswith("execute "):
        return None
    
    # Dictionary mapping execute keywords to number of arguments they take
    execute_keywords: dict[str, Any] = {
        "as": 1,
        "at": 1,
        "positioned": 3,
        "anchored": 1,
        "align": 1,
        "rotated": 2,
        "facing": None,  # Special case: variable arguments
        "in": 1,
    }
    
    def parse_selector_or_argument(parts: list[str], start_index: int) -> tuple[str, int]:
        """ Parse a selector that might contain square brackets or a simple argument.
        
        Args:
            parts (list[str]): The split command parts
            start_index (int): Index to start parsing from
            
        Returns:
            tuple[str, int]: The parsed argument and the next index to continue from
        """
        if start_index >= len(parts):
            return "", start_index
            
        arg = parts[start_index]
        next_index = start_index + 1

        # If not [, we assume it's a simple argument
        if "[" not in arg and arg.startswith("@"):
            return arg, next_index
        
        # If the argument contains [ but doesn't end with ], we need to collect more parts
        if "[" in arg and not arg.endswith("]"):
            # Keep collecting parts until we find one that ends with ]
            while next_index < len(parts) and not arg.endswith("]"):
                arg += " " + parts[next_index]
                next_index += 1
        
        # Clean up the selector by removing spaces after commas
        arg = arg.replace(", ", ",")
        
        # Simplify specific selector arguments if they exist
        if "[" in arg and "]" in arg:
            # Replace tag=!value with tag=!... (negative tags first)
            arg = re.sub(r'tag=![^,\]]+', 'tag=!...', arg)
            
            # Replace tag=value with tag=... (positive tags)
            arg = re.sub(r'tag=[^,\]!][^,\]]*', 'tag=...', arg)
            
            # Replace predicate=!value with predicate=!... (negative predicates)
            arg = re.sub(r'predicate=![^,\]]+', 'predicate=!...', arg)
            
            # Replace predicate=value with predicate=... (positive predicates)
            arg = re.sub(r'predicate=[^,\]!][^,\]]*', 'predicate=...', arg)
            
            # Replace nbt=!value with nbt=!... (negative nbts)
            arg = re.sub(r'nbt=![^,\]]+', 'nbt=!{...}', arg)
            
            # Replace nbt=value with nbt=... (positive nbts)
            arg = re.sub(r'nbt=[^,\]!][^,\]]*', 'nbt={...}', arg)
        
        return arg, next_index
    
    # Parse execute command components
    parts = line.split()
    context_parts = []
    
    i = 1  # Skip "execute"
    while i < len(parts):
        part = parts[i]
        
        if part == "run":
            # We've reached the end of the execute subcommands
            break
        elif part in execute_keywords:
            arg_count = execute_keywords[part]
            
            if part == "facing":
                # Special handling for facing command
                if i + 1 < len(parts) and parts[i + 1] == "entity":
                    if i + 3 < len(parts):
                        context_parts.append(f"facing entity {parts[i + 2]} {parts[i + 3]}")
                        i += 4
                    else:
                        i += 1
                else:
                    # facing coordinates
                    if i + 3 < len(parts):
                        context_parts.append(f"facing {parts[i + 1]} {parts[i + 2]} {parts[i + 3]}")
                        i += 4
                    else:
                        i += 1
            elif part == "positioned":
                # Special handling for positioned (can have 1 or 3 args)
                if i + 3 < len(parts):
                    context_parts.append(f"positioned {parts[i + 1]} {parts[i + 2]} {parts[i + 3]}")
                    i += 4
                elif i + 1 < len(parts):
                    # Handle "positioned ~" or selector cases
                    context_parts.append(f"positioned {parts[i + 1]}")
                    i += 2
                else:
                    i += 1
            elif part in ["as", "at"]:
                # Special handling for selectors that might contain square brackets
                if i + 1 < len(parts):
                    selector, next_i = parse_selector_or_argument(parts, i + 1)
                    context_parts.append(f"{part} {selector}")
                    i = next_i
                else:
                    i += 1
            else:
                # Standard handling for keywords with fixed argument count
                if i + arg_count < len(parts):
                    args = " ".join(parts[i + 1:i + 1 + arg_count])
                    context_parts.append(f"{part} {args}")
                    i += 1 + arg_count
                else:
                    i += 1
        else:
            # Unknown keyword, skip it
            i += 1
    
    if context_parts:
        return " & ".join(context_parts)
    return None
