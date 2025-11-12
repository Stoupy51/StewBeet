"""
Macro argument parsing utilities for Minecraft function headers.

This module handles extracting macro variables from function content
by finding lines that start with '$' and extracting $(variable_name) patterns.
"""

# Imports
import re


# Functions
def extract_macro_variables(content: str) -> list[str]:
    """ Extract all macro variables from function content.

    Args:
        content (str): The function content

    Returns:
        list[str]: List of unique macro variable names found in the content, in order of first appearance

    Examples:
        Basic example:
        >>> content = '''
        ... $execute if score @s temp matches $(slot) run say Found
        ... $data modify entity @s Items[{Slot:$(slot)b}].id set value "$(id)"
        ... $give @p $(id) $(count)
        ... '''
        >>> extract_macro_variables(content)
        ['slot', 'id', 'count']

        From StardustFragment teleport_to:
        >>> content = '$execute in $(dimension) run tp @s $(x) $(y).6 $(z) $(yaw) $(pitch)'
        >>> extract_macro_variables(content)
        ['dimension', 'x', 'y', 'z', 'yaw', 'pitch']

        From SimplEnergy get_max_stack_size:
        >>> content = '''
        ... $execute if items entity @s container.$(result) *[minecraft:max_stack_size=64] run return 64
        ... $execute if items entity @s container.$(result) *[minecraft:max_stack_size=16] run return 16
        ... '''
        >>> extract_macro_variables(content)
        ['result']

        From SimplEnergy update_energy_lore with multiple vars:
        >>> content = '$data modify storage energy:temp list[0] value [$(part_1),$(part_2),$(scale)]'
        >>> extract_macro_variables(content)
        ['part_1', 'part_2', 'scale']
    """
    # Preserve first-occurrence order of macro variables as they appear in the
    # function content. Using a list and membership checks keeps the order
    # stable and mirrors what the user sees in the source file.
    macro_vars: list[str] = []

    # Split content into lines
    lines: list[str] = content.split("\n")

    for line in lines:
        # Check if line starts with '$' (after stripping whitespace and comments)
        stripped: str = line.strip()
        if stripped.startswith("$"):
            # Find all $(variable_name) patterns in the line
            matches: list[str] = re.findall(r'\$\((\w+)\)', line)
            for m in matches:
                if m not in macro_vars:
                    macro_vars.append(m)

    return macro_vars


def is_macro_function(content: str) -> bool:
    """ Check if a function is a macro function.

    A function is considered a macro function if it contains at least one line
    that starts with '$'.

    Args:
        content (str): The function content

    Returns:
        bool: True if the function is a macro function, False otherwise

    Examples:
        Non-macro function:
        >>> is_macro_function("say Hello")
        False

        Simple macro:
        >>> is_macro_function("$say $(message)")
        True

        Macro with comment:
        >>> is_macro_function("# Comment\\n$execute run say $(text)")
        True

        From StardustFragment:
        >>> is_macro_function("$execute in $(dimension) run tp @s $(x) $(y) $(z)")
        True

        From SimplEnergy:
        >>> is_macro_function("$execute if items entity @s container.$(result) *[max_stack_size=64] run return 64")
        True
    """
    lines: list[str] = content.split("\n")
    for line in lines:
        stripped: str = line.strip()
        if stripped.startswith("$"):
            return True
    return False
