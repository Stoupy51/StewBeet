"""
Type inference utilities for macro function arguments.

This module handles inferring the types of macro arguments by analyzing
how functions are called in the @within list.
"""

# Imports
import re

from .object import Header

# Type mapping for NBT suffixes
NBT_TYPE_MAP = {
    "b": "byte",
    "s": "short",
    "": "int",  # No suffix means int
    "l": "long",
    "f": "float",
    "d": "double",
}


def parse_nbt_compound(nbt_string: str) -> dict[str, tuple[str, str]]:
    """ Parse an NBT compound string to extract variable names and their types.

    Args:
        nbt_string (str): The NBT compound string (e.g., '{"id":"hello",Slot:1b,count:1}')

    Returns:
        dict[str, tuple[str, str]]: Dictionary mapping variable names to (value, type) tuples

    Examples:
        Basic types:
        >>> parse_nbt_compound('{"id":"hello",Slot:1b,count:1,price:10.0f}')
        {'id': ('hello', 'string'), 'Slot': ('1', 'byte'), 'count': ('1', 'int'), 'price': ('10.0', 'float')}

        From StardustFragment teleport_to storage call:
        >>> parse_nbt_compound('{x:0,y:0,z:0,yaw:0.0f,pitch:0.0f,dimension:"minecraft:overworld"}')
        {'x': ('0', 'int'), 'y': ('0', 'int'), 'z': ('0', 'int'), 'yaw': ('0.0', 'float'), 'pitch': ('0.0', 'float'), 'dimension': ('minecraft:overworld', 'string')}

        From SimplEnergy with mixed types:
        >>> parse_nbt_compound('{part_1:100,part_2:50,scale:"kJ"}')
        {'part_1': ('100', 'int'), 'part_2': ('50', 'int'), 'scale': ('kJ', 'string')}

        Compound and list types:
        >>> result = parse_nbt_compound('{config:{duration:20,power:1.5f},items:[1,2,3]}')
        >>> result['config'][1]
        'compound'
        >>> result['items'][1]
        'list'
    """
    result: dict[str, tuple[str, str]] = {}

    # Remove outer braces and split by commas (but not commas inside nested structures)
    nbt_string = nbt_string.strip()
    if nbt_string.startswith("{") and nbt_string.endswith("}"):
        nbt_string = nbt_string[1:-1]

    # Simple parser for key:value pairs
    # This is a simplified version that handles basic cases
    # Pattern to match key:value pairs - handles spaces after colons and commas
    # Split by commas first, but be careful about nested structures
    pairs: list[str] = []
    current_pair: str = ""
    depth: int = 0
    in_quotes: bool = False
    quote_char: str = ""

    for char in nbt_string:
        if char in ['"', "'"]:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = ""
        elif char in ['{', '['] and not in_quotes:
            depth += 1
        elif char in ['}', ']'] and not in_quotes:
            depth -= 1
        elif char == ',' and depth == 0 and not in_quotes:
            pairs.append(current_pair.strip())
            current_pair = ""
            continue

        current_pair += char

    if current_pair.strip():
        pairs.append(current_pair.strip())

    # Now parse each pair
    for pair in pairs:
        # Match key:value with optional spaces and optional quotes around keys
        match = re.match(r'["\']?(\w+)["\']?\s*:\s*(.+)', pair)
        if not match:
            continue

        key: str
        value: str
        key, value = match.groups()
        value = value.strip()

        # String values (quoted)
        if value.startswith('"') or value.startswith("'"):
            result[key] = (value.strip('"\''), "string")
        # Compound values (nested {})
        elif value.startswith("{"):
            result[key] = (value, "compound")
        # List values ([])
        elif value.startswith("["):
            result[key] = (value, "list")
        # Numeric values
        else:
            # Check for numeric suffix
            numeric_match = re.match(r'([-+]?\d+\.?\d*)([bslfd]?)', value)
            if numeric_match:
                num_value: str
                suffix: str
                num_value, suffix = numeric_match.groups()
                suffix = suffix.lower()
                num_type: str

                # If no suffix, infer from the value
                if not suffix:
                    # Check if it has a decimal point
                    if '.' in num_value:
                        # Default to double for decimal numbers without suffix
                        num_type = "double"
                    else:
                        # Default to int for whole numbers without suffix
                        num_type = "int"
                else:
                    num_type = NBT_TYPE_MAP.get(suffix, "int")

                result[key] = (num_value, num_type)
            else:
                # Unknown type
                result[key] = (value, "unknown")

    return result


def infer_types_from_direct_call(call_string: str, macro_vars: list[str], all_functions: dict[str, Header]) -> dict[str, str]:
    """ Infer macro argument types from a direct function call with parameters.

    Args:
        call_string (str): The function call string (e.g., 'function my_func {"id":"hello",Slot:1b}')
        macro_vars (list[str]): List of macro variable names to look for
        all_functions (dict[str, Header]): Dictionary of all functions for lookup

    Returns:
        dict[str, str]: Dictionary mapping variable names to their inferred types

    Examples:
        Basic direct call:
        >>> infer_types_from_direct_call('function test {"id":"hello",Slot:1b,count:1}', ['id', 'Slot', 'count'], {})
        {'id': 'string', 'Slot': 'byte', 'count': 'int'}

        From SimplEnergy pulverizer call:
        >>> infer_types_from_direct_call('simplenergy:custom_blocks/pulverizer/gui_active_slot {"result":15}', ['result'], {})
        {'result': 'int'}

        With float values (like StardustFragment):
        >>> infer_types_from_direct_call('function test {x:100,y:64,z:-200,yaw:45.0f,pitch:-10.5f}', ['x', 'y', 'z', 'yaw', 'pitch'], {})
        {'x': 'int', 'y': 'int', 'z': 'int', 'yaw': 'float', 'pitch': 'float'}
    """
    types: dict[str, str] = {}

    # Find the NBT compound in the call string
    # It should be after "function <path> " or just after the function path
    # Handle both direct calls and @within entries
    match = re.search(r'(?:function\s+\S+\s+)?({.+})', call_string)
    if match:
        nbt_string: str = match.group(1)
        parsed: dict[str, tuple[str, str]] = parse_nbt_compound(nbt_string)

        # Map the parsed types to our macro variables
        for var in macro_vars:
            if var in parsed:
                value: str
                var_type: str
                value, var_type = parsed[var]

                # Check if the value is a macro variable reference (e.g., $(other_var))
                macro_ref_match = re.match(r'\$\((\w+)\)', value)
                if macro_ref_match:
                    # This is a reference to another macro variable
                    # Try to find the type from the calling function
                    caller_match = re.match(r'([^\s]+)', call_string)
                    if caller_match:
                        caller_func = caller_match.group(1)
                        if caller_func in all_functions:
                            caller_args = all_functions[caller_func].args
                            ref_var = macro_ref_match.group(1)
                            if ref_var in caller_args:
                                # caller_args[ref_var] is a tuple (type, description_lines)
                                # We only need the type (first element)
                                types[var] = caller_args[ref_var][0]
                            else:
                                types[var] = var_type
                        else:
                            types[var] = var_type
                else:
                    types[var] = var_type

    return types


def infer_types_from_storage_call(within_list: list[str], macro_vars: list[str], all_functions: dict[str, Header]) -> dict[str, str]:
    """ Infer macro argument types by looking at 'with storage' calls and the caller's content.

    Args:
        within_list (list[str]): List of functions/contexts that call this function
        macro_vars (list[str]): List of macro variable names to infer types for
        all_functions (dict[str, Header]): Dictionary of all functions for lookup

    Returns:
        dict[str, str]: Dictionary mapping variable names to their inferred types

    Examples:
        >>> # This would need actual function content to work properly
        >>> infer_types_from_storage_call(['test:caller with storage temp macro'], ['id', 'count'], {})
        {}
    """
    types: dict[str, str] = {}

    for caller in within_list:
        # Check if this is a storage call
        if "with storage" in caller or "with entity" in caller:
            # Extract the caller function name
            caller_func: str = caller.split()[0]

            # Look up the caller function
            if caller_func in all_functions:
                caller_content: str = all_functions[caller_func].content

                # Look for data modify commands that set up the storage
                # Pattern: data modify storage <storage_path> [<path...>] set value {<nbt>}
                # Some usages include additional path components between the storage id and 'set',
                # for example: `data modify storage stardust:temp macro set value {...}`
                # so we allow optional tokens between the storage path and the 'set' keyword.
                storage_pattern: str = r'data\s+modify\s+storage\s+\S+(?:\s+\S+)*\s+set\s+value\s+({.+?})'
                matches: list[str] = re.findall(storage_pattern, caller_content, flags=re.DOTALL)

                for nbt_string in matches:
                    parsed: dict[str, tuple[str, str]] = parse_nbt_compound(nbt_string)
                    for var in macro_vars:
                        if var in parsed and var not in types:
                            types[var] = parsed[var][1]

    return types


def infer_macro_types(header: Header, all_functions: dict[str, Header]) -> dict[str, str]:
    """ Infer types for all macro variables in a function.

    Args:
        header (Header): The function header containing content and @within info
        all_functions (dict[str, Header]): Dictionary of all functions for lookup

    Returns:
        dict[str, str]: Dictionary mapping variable names to their inferred types

    Examples:
        Direct call with NBT (SimplEnergy style):
        >>> header = Header("test:func", ["test:caller {id:'hello',count:1}"], [], "$give @p $(id) $(count)")
        >>> infer_macro_types(header, {})
        {'id': 'string', 'count': 'int'}

        Storage call (StardustFragment style):
        >>> caller_content = 'data modify storage test:temp macro set value {x:0,y:64,z:0}\\nfunction test:target with storage test:temp macro'
        >>> caller = Header("test:caller", [], [], caller_content)
        >>> target = Header("test:target", ["test:caller with storage test:temp macro"], [], "$tp @s $(x) $(y) $(z)")
        >>> infer_macro_types(target, {"test:caller": caller})
        {'x': 'int', 'y': 'int', 'z': 'int'}

        Multiple types (like SimplEnergy energy lore):
        >>> header = Header("test:lore", ["test:main {part_1:100,part_2:50,scale:'kJ'}"], [], "$say $(part_1).$(part_2)$(scale)")
        >>> infer_macro_types(header, {})
        {'part_1': 'int', 'part_2': 'int', 'scale': 'string'}
    """
    from .macro_parser import extract_macro_variables

    # Extract macro variables
    macro_vars: list[str] = extract_macro_variables(header.content)
    if not macro_vars:
        return {}

    types: dict[str, str] = {}

    # First pass: Check for direct calls with parameters
    for caller in header.within:
        direct_types: dict[str, str] = infer_types_from_direct_call(caller, macro_vars, all_functions)
        for var, var_type in direct_types.items():
            if var not in types:
                types[var] = var_type

    # Second pass: Check for storage-based calls
    storage_types: dict[str, str] = infer_types_from_storage_call(header.within, macro_vars, all_functions)
    for var, var_type in storage_types.items():
        if var not in types:
            types[var] = var_type

    # Fill in unknowns for variables we couldn't infer
    for var in macro_vars:
        if var not in types:
            types[var] = "unknown"

    return types
