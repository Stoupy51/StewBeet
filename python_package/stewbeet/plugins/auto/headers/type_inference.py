"""
Type inference utilities for macro function arguments.

This module handles inferring the types of macro arguments by analyzing
how functions are called in the @within list.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import re

from .object import Header

WITHIN_CALLER_RE: re.Pattern[str] = re.compile(r"(?:string in )?([^\s{]+)")
""" Isolates the function path at the head of a @within entry.
It skips the optional "string in " prefix and stops before the macro payload or context.
"""

ESCAPED_QUOTE_RE: re.Pattern[str] = re.compile(r'\\(["\'])')
""" Matches a backslash-escaped quote.
Payloads read from inside a JSON string (tellraw / dialog run_command) carry them, e.g. {jump:\\"green\\"}.
"""

NBT_PAIR_RE: re.Pattern[str] = re.compile(r'["\']?(\w+)["\']?\s*:\s*(.+)')
""" A key:value pair of a compound, the key possibly quoted. """

NBT_NUMBER_RE: re.Pattern[str] = re.compile(r'([-+]?\d+\.?\d*)([bslfd]?)')
""" A number and its type suffix. """

MACRO_REF_RE: re.Pattern[str] = re.compile(r'\$\((\w+)\)')
""" A value that is another macro variable, `$(name)`. """

STORAGE_SET_RE: re.Pattern[str] = re.compile(r'data\s+modify\s+storage\s+\S+(?:\s+\S+)*\s+set\s+value\s+({.+?})', flags=re.DOTALL)
""" A compound set into a storage, `data modify storage stardust:temp macro set value {...}`, the path tokens optional. """

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
	""" Variable names of an NBT compound string mapped to their (value, type).

	>>> parse_nbt_compound('{"id":"hello",Slot:1b,count:1,price:10.0f}')
	{'id': ('hello', 'string'), 'Slot': ('1', 'byte'), 'count': ('1', 'int'), 'price': ('10.0', 'float')}
	>>> parse_nbt_compound(r'{jump:\\"green\\",delay:20}')  # Inside a JSON string, quotes arrive escaped
	{'jump': ('green', 'string'), 'delay': ('20', 'int')}
	"""
	nbt_string = ESCAPED_QUOTE_RE.sub(r"\1", nbt_string.strip())
	if nbt_string.startswith("{") and nbt_string.endswith("}"):
		nbt_string = nbt_string[1:-1]
	result: dict[str, tuple[str, str]] = {}
	for pair in split_top_level(nbt_string):
		match: re.Match[str] | None = NBT_PAIR_RE.match(pair)
		if match:
			result[match[1]] = nbt_value(match[2].strip())
	return result


def split_top_level(text: str) -> list[str]:
	""" The parts of `text` between the commas outside nested structures and quotes, stripped.

	>>> split_top_level('a:1, b:{c:2,d:3},e:"f,g"')
	['a:1', 'b:{c:2,d:3}', 'e:"f,g"']
	"""
	pairs: list[str] = []
	current: str = ""
	depth: int = 0
	quote: str = ""
	for char in text:
		if char in ('"', "'"):
			if not quote:
				quote = char
			elif char == quote:
				quote = ""
		elif not quote and char in ('{', '['):
			depth += 1
		elif not quote and char in ('}', ']'):
			depth -= 1
		elif not quote and char == ',' and depth == 0:
			pairs.append(current.strip())
			current = ""
			continue
		current += char
	if current.strip():
		pairs.append(current.strip())
	return pairs


def nbt_value(value: str) -> tuple[str, str]:
	""" A value as written without its quotes or suffix, and its type, from its quotes, brackets or numeric suffix.

	>>> nbt_value("'kJ'"), nbt_value("1.5f"), nbt_value("2.0"), nbt_value("[1]"), nbt_value("???")
	(('kJ', 'string'), ('1.5', 'float'), ('2.0', 'double'), ('[1]', 'list'), ('???', 'unknown'))
	"""
	if value.startswith(('"', "'")):
		return value.strip('"\''), "string"
	if value.startswith("{"):
		return value, "compound"
	if value.startswith("["):
		return value, "list"
	numeric: re.Match[str] | None = NBT_NUMBER_RE.match(value)
	if not numeric:
		return value, "unknown"
	num_value, suffix = numeric[1], numeric[2].lower()
	return num_value, NBT_TYPE_MAP.get(suffix, "int") if suffix else ("double" if "." in num_value else "int")


def infer_types_from_direct_call(call_string: str, macro_vars: list[str], all_functions: dict[str, Header]) -> dict[str, str]:
	""" Infer macro argument types from a direct function call passing an NBT compound.

	>>> infer_types_from_direct_call('function test {"id":"hello",Slot:1b,count:1}', ['id', 'Slot', 'count'], {})
	{'id': 'string', 'Slot': 'byte', 'count': 'int'}
	"""
	# The NBT compound follows "function <path> " in direct calls, or the path alone in @within entries
	match: re.Match[str] | None = re.search(r'(?:function\s+\S+\s+)?({.+})', call_string)
	if not match:
		return {}
	parsed: dict[str, tuple[str, str]] = parse_nbt_compound(match.group(1))
	types: dict[str, str] = {}
	for var in macro_vars:
		if var in parsed:
			inferred: str | None = passed_type(*parsed[var], call_string, all_functions)
			if inferred is not None:
				types[var] = inferred
	return types


def passed_type(value: str, var_type: str, call_string: str, all_functions: dict[str, Header]) -> str | None:
	""" The type of a value a call passes, a `$(name)` reference taking the type the calling function gives its own `name`.

	A quoted reference is an explicit string. None when the caller cannot be read off `call_string`.

	>>> callers = {"t:c": Header("t:c", args={"n": ("int", [])})}
	>>> passed_type("$(n)", "unknown", "t:c {x:$(n)}", callers), passed_type("$(n)", "string", "t:c", callers)
	('int', 'string')
	"""
	reference: re.Match[str] | None = MACRO_REF_RE.match(value)
	if reference is None or var_type == "string":
		return var_type
	caller: re.Match[str] | None = WITHIN_CALLER_RE.match(call_string)
	if caller is None:
		return None
	caller_args: dict[str, tuple[str, list[str]]] = all_functions[caller[1]].args if caller[1] in all_functions else {}
	return caller_args[reference[1]][0] if reference[1] in caller_args else var_type


def infer_types_from_storage_call(within_list: list[str], macro_vars: list[str], all_functions: dict[str, Header]) -> dict[str, str]:
	""" Infer macro argument types from the compounds a caller using `with storage` or `with entity` sets into a storage.

	The first compound giving a variable decides its type.

	>>> # This would need actual function content to work properly
	>>> infer_types_from_storage_call(['test:caller with storage temp macro'], ['id', 'count'], {})
	{}
	"""
	types: dict[str, str] = {}
	for caller in within_list:
		if "with storage" not in caller and "with entity" not in caller:
			continue
		caller_match: re.Match[str] | None = WITHIN_CALLER_RE.match(caller)
		caller_func: str = caller_match.group(1) if caller_match else ""
		if caller_func not in all_functions:
			continue
		for nbt_string in STORAGE_SET_RE.findall(all_functions[caller_func].content):
			parsed: dict[str, tuple[str, str]] = parse_nbt_compound(nbt_string)
			types.update({var: parsed[var][1] for var in macro_vars if var in parsed and var not in types})
	return types


def infer_macro_types(header: Header, all_functions: dict[str, Header]) -> dict[str, str]:
	""" Infer the type of every macro variable of a function from its callers, direct or through a storage.

	>>> header = Header("test:func", ["test:caller {id:'hello',count:1}"], [], "$give @p $(id) $(count)")
	>>> infer_macro_types(header, {})
	{'id': 'string', 'count': 'int'}
	>>> # An unparsable caller never shadows a later caller that does spell the type out
	>>> header = Header("test:list", ["test:menu {jump:???}", 'test:remove {jump:"$(jump)"}'], [], "$say $(jump)")
	>>> infer_macro_types(header, {})
	{'jump': 'string'}
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
			if types.get(var, "unknown") == "unknown":
				types[var] = var_type

	# Second pass: Check for storage-based calls
	storage_types: dict[str, str] = infer_types_from_storage_call(header.within, macro_vars, all_functions)
	for var, var_type in storage_types.items():
		if types.get(var, "unknown") == "unknown":
			types[var] = var_type

	# Fill in unknowns for variables we couldn't infer
	for var in macro_vars:
		if var not in types:
			types[var] = "unknown"

	return types


__test__: dict[str, str] = {
	"infer_macro_types": """
	>>> caller_content = (
	...     'data modify storage test:temp macro set value {x:0,y:64,z:0}\\n'
	...     'function test:target with storage test:temp macro'
	... )
	>>> caller = Header("test:caller", [], [], caller_content)
	>>> target = Header("test:target", ["test:caller with storage test:temp macro"], [], "$tp @s $(x) $(y) $(z)")
	>>> infer_macro_types(target, {"test:caller": caller})
	{'x': 'int', 'y': 'int', 'z': 'int'}
	>>> header = Header("test:lore", ["test:main {part_1:100,part_2:50,scale:'kJ'}"], [], "$say $(part_1).$(part_2)$(scale)")
	>>> infer_macro_types(header, {})
	{'part_1': 'int', 'part_2': 'int', 'scale': 'string'}
	""",
	"infer_types_from_direct_call": """
	>>> infer_types_from_direct_call('simplenergy:custom_blocks/pulverizer/gui_active_slot {"result":15}', ['result'], {})
	{'result': 'int'}
	>>> infer_types_from_direct_call(
	...     'function test {x:100,y:64,z:-200,yaw:45.0f,pitch:-10.5f}', ['x', 'y', 'z', 'yaw', 'pitch'], {}
	... )
	{'x': 'int', 'y': 'int', 'z': 'int', 'yaw': 'float', 'pitch': 'float'}
	""",
	"parse_nbt_compound": """
	>>> for name, parsed in parse_nbt_compound('{x:0,y:0,z:0,yaw:0.0f,pitch:0.0f,dimension:"minecraft:overworld"}').items():
	...     print(name, parsed)
	x ('0', 'int')
	y ('0', 'int')
	z ('0', 'int')
	yaw ('0.0', 'float')
	pitch ('0.0', 'float')
	dimension ('minecraft:overworld', 'string')
	>>> parse_nbt_compound('{part_1:100,part_2:50,scale:"kJ"}')
	{'part_1': ('100', 'int'), 'part_2': ('50', 'int'), 'scale': ('kJ', 'string')}
	>>> result = parse_nbt_compound('{config:{duration:20,power:1.5f},items:[1,2,3]}')
	>>> result['config'][1]
	'compound'
	>>> result['items'][1]
	'list'
	""",
}

