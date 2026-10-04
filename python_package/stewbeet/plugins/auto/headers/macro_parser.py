"""
Macro argument parsing utilities for Minecraft function headers.

This module handles extracting macro variables from function content
by finding lines that start with '$' and extracting $(variable_name) patterns.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import re

import stouputils as stp


# Functions
def extract_macro_variables(content: str) -> list[str]:
	""" Unique macro variable names of a function content, in order of first appearance.

	>>> content = '$data modify storage energy:temp list[0] value [$(part_1),$(part_2),$(scale)]'
	>>> extract_macro_variables(content)
	['part_1', 'part_2', 'scale']
	"""
	# Preserve first-occurrence order of macro variables as they appear in the function content.
	# Using a list and membership checks keeps the order stable and mirrors what the user sees in the source file.
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


@stp.simple_cache
def is_macro_function(content: str) -> bool:
	""" Whether a function content holds at least one macro line, starting with '$'.

	>>> is_macro_function("say Hello")
	False
	>>> is_macro_function("$say $(message)")
	True
	"""
	return "$" in content and any(line.lstrip().startswith("$") for line in content.split("\n"))


__test__: dict[str, str] = {
	"extract_macro_variables": """
	>>> content = '''
	... $execute if score @s temp matches $(slot) run say Found
	... $data modify entity @s Items[{Slot:$(slot)b}].id set value "$(id)"
	... $give @p $(id) $(count)
	... '''
	>>> extract_macro_variables(content)
	['slot', 'id', 'count']
	>>> content = '$execute in $(dimension) run tp @s $(x) $(y).6 $(z) $(yaw) $(pitch)'
	>>> extract_macro_variables(content)
	['dimension', 'x', 'y', 'z', 'yaw', 'pitch']
	>>> content = '''
	... $execute if items entity @s container.$(result) *[minecraft:max_stack_size=64] run return 64
	... $execute if items entity @s container.$(result) *[minecraft:max_stack_size=16] run return 16
	... '''
	>>> extract_macro_variables(content)
	['result']
	""",
	"is_macro_function": """
	>>> is_macro_function("# Comment\\n$execute run say $(text)")
	True
	>>> is_macro_function("$execute in $(dimension) run tp @s $(x) $(y) $(z)")
	True
	>>> is_macro_function("$execute if items entity @s container.$(result) *[max_stack_size=64] run return 64")
	True
	""",
}

