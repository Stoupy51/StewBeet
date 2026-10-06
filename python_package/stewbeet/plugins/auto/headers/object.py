
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import re

# Constants
ARG_WITH_DESCRIPTION: re.Pattern[str] = re.compile(r'(\w+)\s*\((\w+)\)\s*:\s*(.+)')
""" An argument line of `@args`: `name (type): description`. """

ARG: re.Pattern[str] = re.compile(r'(\w+)\s*\((\w+)\)')
""" An argument line of `@args` without a description: `name (type)`. """


# Header class
class Header:
	""" A class representing a function header.

	>>> header = Header("test:function", ["other:function"], ["Some info"], "say Hello")
	>>> header.path
	'test:function'
	>>> header.within
	['other:function']
	>>> header.other
	['Some info']
	>>> header.content
	'say Hello'
	"""
	__slots__ = {
		"args": "Dictionary mapping macro argument names to (type, description_lines), "
				"where description_lines is a list of strings (empty list if no description)",
		"content": "The content of the function",
		"executed": "The execution context (ex: \"as the player & at current position\")",
		"other": "List of other information about the function",
		"path": "The path to the function (ex: \"namespace:folder/function_name\")",
		"within": "List of functions that call this function",
	}

	def __init__(
		self,
		path: str,
		within: list[str] | None = None,
		other: list[str] | None = None,
		content: str = "",
		executed: str | None = None,
		args: dict[str, tuple[str, list[str]]] | None = None
	):
		self.path = path
		self.within = within or []
		self.other = other or []
		self.content = content
		self.executed = executed or ""
		self.args = args or {}

	@classmethod
	def from_content(cls, path: str, content: str) -> Header:
		""" Create a Header object from a function's content, parsing the ``#>`` block at its top.

		>>> content = "#> test:function\\n#\\n# @within\\tother:function\\n# Some info\\n#\\nsay Hello"
		>>> header = Header.from_content("test:function", content)
		>>> header.within, header.other, header.content
		(['other:function'], ['Some info'], 'say Hello')
		"""
		actual_content: str = content.strip()
		if not actual_content.startswith("#> "):
			return cls(path, [], [], actual_content, "", {})

		# Skip the first line (#> path) and the second line (#)
		lines: list[str] = actual_content.split("\n")
		i: int = 2
		executed: str = ""
		if i < len(lines) and lines[i].strip().startswith("# @executed"):
			executed = lines[i].strip().split("@executed")[1].strip()
			i += 1
		i = skip_empty_comments(lines, i)

		args: dict[str, tuple[str, list[str]]] = {}
		if i < len(lines) and lines[i].strip().startswith("# @args"):
			i = read_args(lines, i, args)
		i = skip_empty_comments(lines, i)

		within: list[str] = []
		while i < len(lines) and lines[i].strip().startswith("# @within"):
			if lines[i].strip() != "# @within":
				within.append(lines[i].strip().split("@within")[1].strip())
			i += 1
		i = skip_empty_comments(lines, i)

		# Every comment line left, empty ones included, is other information
		other: list[str] = []
		while i < len(lines) and lines[i].strip().startswith("#"):
			other.append(lines[i].strip()[2:])
			i += 1
		if other and other[-1] == "":
			other.pop()
		return cls(path, within, other, "\n".join(lines[i:]).strip(), executed, args)

	def to_str(self) -> str:
		""" Convert the Header object to the function content with its header.

		>>> content = '''
		... #> test:function
		... #
		... # @within\\tother:function
		... #
		... # Some info
		... #
		...
		... say Hello\\n\\n'''
		>>> header = Header("test:function", ["other:function"], ["Some info"], "say Hello")
		>>> content.strip() == header.to_str().strip()
		True
		"""
		# Start with the path
		header: str = f"\n#> {self.path}\n#\n"

		# Add the executed context (only if known)
		if self.executed:
			executed: str = self.executed.strip()
			executed: str = "".join(
				x for i, x in enumerate(executed)
				if x != " " or (i > 0 and executed[i - 1] not in ":,")
			)
			header += f"# @executed\t{executed}\n#\n"

		# Add the within list
		if self.within:
			header += "# @within\t" + "\n#\t\t\t".join(self.within) + "\n#\n"
		else:
			header += "# @within\t???\n#\n"

		# The arguments in the order they were first introduced
		if self.args:
			header += "# @args\t\t" + "\n#\t\t\t".join(self.arg_lines()) + "\n#\n"

		# Add other information
		for line in self.other:
			header += f"# {line}\n"

		# Add final empty line and content
		if not header.endswith("#\n"):
			header += "#\n"
		return (header + "\n" + self.content.strip() + "\n\n").replace("\n\n\n", "\n\n")

	def arg_lines(self) -> list[str]:
		""" One `name (type): description` line per argument, the further lines of a compound's description indented under it. """
		lines: list[str] = []
		for arg_name, (arg_type, description_lines) in self.args.items():
			if not description_lines:
				lines.append(f"{arg_name} ({arg_type})")
				continue
			lines.append(f"{arg_name} ({arg_type}): {description_lines[0]}")
			lines.extend(f"\t\t\t\t{desc_line}" for desc_line in description_lines[1:])
		return lines

if __name__ == "__main__":
	# Example usage
	example_content = """
#> alt_launch
#
# @executed			as the player & at current position
#
# @args				target (string): target selector for position and rotation source
#					time (int): time in ticks
#					with (compound): additional arguments (optional)
#						- yaw : float - yaw rotation (will override target rotation)
#						- pitch : float - pitch rotation (will override target rotation)
#						- go_side : float - how far to go side (0 = don't go side)
#						- add_y : float - additional y position (default: 20.0)
#						- particle : int - particle effect (0 = none, 1 = glow)
#						- interpolation : int - teleport duration (default: 1)
#						- delay : int - delay in ticks before starting (default: 0)
#
# @description		Launch a cinematic that moves the player to the position and rotation of a target entity
#
# @example			/execute as @s positioned 0 69 0 rotated -55 10 run function switch:cinematic/alt_launch {target:"@s",time:60,with:{go_side:1,add_y:20.0,particle:1,interpolation:1,delay:20}}
#

# Fonction content here
"""  # noqa: E501
	header = Header.from_content("alt_launch", example_content)
	print(header.to_str())


__test__: dict[str, str] = {
	"Header.from_content": """
	>>> content = '''
	... #> test:function
	... #
	... # @within    other:function
	... # Some info
	... #
	... say Hello'''
	>>> header = Header.from_content("test:function", content)
	>>> header.path
	'test:function'
	>>> header.within
	['other:function']
	>>> header.other
	['Some info']
	>>> header.content
	'say Hello'
	>>> tp_header = Header("stardust:dimensions/teleport_to",
	...                    ["stardust:dimensions/teleport_home with storage stardust:main world_spawn"],
	...                    [],
	...                    "$execute in $(dimension) run tp @s $(x) $(y) $(z)",
	...                    "in stardust:cavern",
	...                    {'dimension': ('string', []), 'x': ('int', []), 'y': ('int', []), 'z': ('int', [])})
	>>> tp_header.executed
	'in stardust:cavern'
	>>> tp_header.args['dimension']
	('string', [])
	>>> tp_header.args['x']
	('int', [])
	>>> len(tp_header.args)
	4
	>>> lore_header = Header("simplenergy:calls/update_energy_lore/macro",
	...                      ["simplenergy:calls/update_energy_lore/main with storage simplenergy:temp macro"],
	...                      [],
	...                      "$data modify storage energy:temp list[0] set value $(part_1)",
	...                      "",
	...                      {'part_1': ('int', ['first part of energy value']),
	...                       'part_2': ('int', ['second part of energy value']),
	...                       'scale': ('string', ['energy scale suffix'])})
	>>> lore_header.args['part_1']
	('int', ['first part of energy value'])
	>>> lore_header.args['part_2']
	('int', ['second part of energy value'])
	>>> lore_header.args['scale']
	('string', ['energy scale suffix'])
	>>> comp_header = Header("test:compound_func",
	...                      [],
	...                      [],
	...                      "function content",
	...                      "",
	...                      {'config': ('compound', ['configuration object',
	...                                                '- duration : int - how long in ticks',
	...                                                '- power : float - effect strength'])})
	>>> comp_header.args['config']
	('compound', ['configuration object', '- duration : int - how long in ticks', '- power : float - effect strength'])
	""",
}


def skip_empty_comments(lines: list[str], i: int) -> int:
	""" The index of the first line from `i` that is not a bare `#`. """
	while i < len(lines) and lines[i].strip() == "#":
		i += 1
	return i


def read_args(lines: list[str], i: int, args: dict[str, tuple[str, list[str]]]) -> int:
	""" Read the `@args` section starting on line `i` into `args`, and return the index of the line after it.

	Each argument is an indented `name (type): description` line, followed by its `- ...` lines for a compound.
	The first one may sit on the `@args` line itself.

	>>> args = {}
	>>> read_args(["# @args\tcount (int): How many", "#\t\t- at least 1", "#\tname (string)", "say"], 0, args), args
	(3, {'count': ('int', ['How many', '- at least 1']), 'name': ('string', [])})
	"""
	current: tuple[str, str, list[str]] | None = parse_arg(re.sub(r'^#\s*@args\s+', '', lines[i].strip()))
	i += 1
	while i < len(lines) and lines[i].strip().startswith("#"):
		line: str = lines[i].strip()
		if len(line) <= 1 or not line[1].isspace():
			break
		text: str = line[1:].strip()
		if not text.startswith("-"):
			if current:
				args[current[0]] = (current[1], current[2][:])
			current = parse_arg(text)
		elif current:
			current[2].append(text)
		i += 1
	if current:
		args[current[0]] = (current[1], current[2][:])
	return i


def parse_arg(text: str) -> tuple[str, str, list[str]] | None:
	""" An argument's name, type and description lines, None when `text` is not an argument.

	>>> parse_arg("count (int): How many"), parse_arg("name (string)"), parse_arg("- a field")
	(('count', 'int', ['How many']), ('name', 'string', []), None)
	"""
	if match := ARG_WITH_DESCRIPTION.match(text):
		return match[1], match[2], [match[3]]
	if match := ARG.match(text):
		return match[1], match[2], []
	return None

