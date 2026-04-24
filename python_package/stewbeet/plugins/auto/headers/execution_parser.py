"""
Execution context parsing utilities for Minecraft function headers.

This module handles parsing execute commands to extract execution contexts
like 'as @e[...] & at @s' from command lines.
"""

# Imports
from stouputils.typing import JsonDict


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
    execute_keywords: JsonDict = {
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

        arg: str = parts[start_index]
        next_index: int = start_index + 1

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
            # Process duplicates and simplify only when multiple occurrences exist
            if "," in arg:
                # Extract the content between [ and ]
                selector_start: int = arg.find("[")
                selector_end: int = arg.rfind("]")
                if selector_start != -1 and selector_end != -1:
                    prefix: str = arg[:selector_start + 1]
                    suffix: str = arg[selector_end:]
                    content: str = arg[selector_start + 1:selector_end]

                    # Split by comma and process each part
                    parts_list: list[str] = [part.strip() for part in content.split(",")]

                    # Count occurrences of each attribute type
                    attribute_counts: dict[str, int] = {}
                    for part in parts_list:
                        if "=" in part:
                            attr_name: str = part.split("=")[0]
                            attribute_counts[attr_name] = attribute_counts.get(attr_name, 0) + 1

                    # Process parts and replace with ... only when there are duplicates
                    processed_parts: list[str] = []
                    seen_attributes: set[str] = set()

                    for part in parts_list:
                        if "=" in part:
                            attr_name: str = part.split("=")[0]
                            attr_value: str = part.split("=", 1)[1]  # Get the full value after the first =

                            # Special handling for NBT - only simplify if longer than 50 characters
                            if attr_name == "nbt":
                                if len(attr_value) > 50:
                                    if part.startswith(attr_name + "=!"):
                                        processed_parts.append(f"{attr_name}=!{{...}}")
                                    else:
                                        processed_parts.append(f"{attr_name}={{...}}")
                                else:
                                    processed_parts.append(part)  # Keep original if <= 50 chars
                            # If this attribute appears multiple times and we haven't processed it yet
                            elif attribute_counts[attr_name] > 1 and attr_name not in seen_attributes:
                                seen_attributes.add(attr_name)
                                # Replace with simplified version
                                if part.startswith(attr_name + "=!"):
                                    # Negative attribute
                                    if attr_name in ["tag", "predicate"]:
                                        processed_parts.append(f"{attr_name}=!...")
                                    else:
                                        processed_parts.append(part)  # Keep original for unknown types
                                else:
                                    # Positive attribute
                                    if attr_name in ["tag", "predicate"]:
                                        processed_parts.append(f"{attr_name}=...")
                                    else:
                                        processed_parts.append(part)  # Keep original for unknown types
                            elif attribute_counts[attr_name] == 1:
                                # Single occurrence, keep as-is (unless it's NBT and was already handled above)
                                if attr_name != "nbt":
                                    processed_parts.append(part)
                            # Skip subsequent occurrences of duplicate attributes (except NBT which is handled separately)
                        else:
                            # Keep non-attribute parts (like dx=0,dy=0,dz=0)
                            processed_parts.append(part)

                    # Rebuild the selector
                    arg = prefix + ",".join(processed_parts) + suffix

        return arg, next_index

    # Parse execute command components
    parts: list[str] = line.split()
    context_parts: list[str] = []

    index: int = 1  # Skip "execute"
    while index < len(parts):
        part = parts[index]

        if part == "run":
            # We've reached the end of the execute subcommands
            break
        elif part in execute_keywords:
            arg_count: int | None = execute_keywords[part]

            if part == "facing":
                # Special handling for facing command
                if index + 1 < len(parts) and parts[index + 1] == "entity":
                    if index + 3 < len(parts):
                        context_parts.append(f"facing entity {parts[index + 2]} {parts[index + 3]}")
                        index += 4
                    else:
                        index += 1
                else:
                    # facing coordinates
                    if index + 3 < len(parts):
                        context_parts.append(f"facing {parts[index + 1]} {parts[index + 2]} {parts[index + 3]}")
                        index += 4
                    else:
                        index += 1
            elif part == "positioned":
                # Special handling for positioned (can have 1 or 3 args)
                if index + 3 < len(parts):
                    context_parts.append(f"positioned {parts[index + 1]} {parts[index + 2]} {parts[index + 3]}")
                    index += 4
                elif index + 1 < len(parts):
                    # Handle "positioned ~" or selector cases
                    context_parts.append(f"positioned {parts[index + 1]}")
                    index += 2
                else:
                    index += 1
            elif part == "at":
                # Special handling for "at @s" - it resets position/rotation context
                if index + 1 < len(parts):
                    selector: str
                    next_i: int
                    selector, next_i = parse_selector_or_argument(parts, index + 1)
                    # Remove any previous position/rotation modifiers when "at" is used
                    context_parts = [cp for cp in context_parts if not any(keyword in cp for keyword in ["positioned", "align", "rotated", "anchored", "in"])]
                    context_parts.append(f"{part} {selector}")
                    index = next_i
                else:
                    index += 1
            elif part == "as":
                # Special handling for selectors that might contain square brackets
                if index + 1 < len(parts):
                    selector, next_i = parse_selector_or_argument(parts, index + 1)
                    context_parts.append(f"{part} {selector}")
                    index = next_i
                else:
                    index += 1
            else:
                # Standard handling for keywords with fixed argument count
                if arg_count is not None and index + arg_count < len(parts):
                    args: str = " ".join(parts[index + 1:index + 1 + arg_count])
                    context_parts.append(f"{part} {args}")
                    index += 1 + arg_count
                else:
                    index += 1
        else:
            # Unknown keyword, skip it
            index += 1

    if context_parts:
        return " & ".join(context_parts)
    return None
