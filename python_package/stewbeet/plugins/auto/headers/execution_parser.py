"""
Execution context parsing utilities for Minecraft function headers.

This module handles parsing execute commands to extract execution contexts
like 'as @e[...] & at @s' from command lines.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections import Counter

# Constants
FIXED_ARGUMENTS: dict[str, int] = {"anchored": 1, "align": 1, "rotated": 2, "in": 1, "facing": 3}
""" Subcommands taking a fixed number of words, `facing entity <target> <anchor>` being three like `facing <x> <y> <z>`. """

POSITION_KEYWORDS: tuple[str, ...] = ("positioned", "align", "rotated", "anchored", "in")
""" Context parts an `at` replaces, matched anywhere in the part. """

SIMPLIFIED_ATTRIBUTES: tuple[str, ...] = ("tag", "predicate")
""" Selector attributes shown as `...` when a selector repeats them. """


# Functions
def parse_execution_context_from_line(line: str) -> str | None:
	""" Execution context of a line calling a function, None for the default one.

	>>> parse_execution_context_from_line("execute as @e[type=zombie] at @s run function test:func")
	'as @e[type=zombie] & at @s'
	>>> None is parse_execution_context_from_line("execute if score @s data matches 1 run function test:func")
	True
	"""
	line = line.strip()
	if not line.startswith("execute "):
		return None
	parts: list[str] = line.split()
	context: list[str] = []
	index: int = 1
	while index < len(parts) and parts[index] != "run":
		index = read_subcommand(parts, index, context)
	return " & ".join(context) or None


def read_subcommand(parts: list[str], index: int, context: list[str]) -> int:
	""" Add the context the subcommand at `index` sets to `context`, and return where the next one starts.

	A subcommand setting no context, or missing its arguments, is skipped one word at a time.
	"""
	part: str = parts[index]
	if part in ("as", "at") and index + 1 < len(parts):
		selector, next_index = read_selector(parts, index + 1)
		if part == "at":
			context[:] = [cp for cp in context if not any(keyword in cp for keyword in POSITION_KEYWORDS)]
		context.append(f"{part} {selector}")
		return next_index

	# `positioned` takes three coordinates, or one word for `positioned as <selector>` and the like
	arg_count: int | None = FIXED_ARGUMENTS.get(part)
	if part == "positioned":
		arg_count = 3 if index + 3 < len(parts) else 1
	if arg_count is None or index + arg_count >= len(parts):
		return index + 1
	context.append(f"{part} {' '.join(parts[index + 1:index + 1 + arg_count])}")
	return index + 1 + arg_count


def read_selector(parts: list[str], start: int) -> tuple[str, int]:
	""" The selector or argument starting at `start`, joined back when its brackets hold spaces, and the index after it.

	>>> read_selector(["@e[tag=a,", "tag=b]", "run"], 0)
	('@e[tag=...]', 2)
	"""
	arg: str = parts[start]
	next_index: int = start + 1
	if "[" not in arg and arg.startswith("@"):
		return arg, next_index
	if "[" in arg:
		while next_index < len(parts) and not arg.endswith("]"):
			arg += " " + parts[next_index]
			next_index += 1
	arg = arg.replace(", ", ",")
	if "[" in arg and "]" in arg and "," in arg:
		arg = simplify_selector(arg)
	return arg, next_index


def simplify_selector(selector: str) -> str:
	""" A selector with its long NBT and its repeated tags and predicates shortened to `...`.

	A repeated attribute keeps its first occurrence only, and an NBT over 50 characters becomes `{...}`.

	>>> simplify_selector("@e[tag=a,tag=!b,type=zombie,nbt={a:1}]")
	'@e[tag=...,type=zombie,nbt={a:1}]'
	"""
	start: int = selector.find("[")
	end: int = selector.rfind("]")
	parts: list[str] = [part.strip() for part in selector[start + 1:end].split(",")]
	counts: Counter[str] = Counter(part.split("=")[0] for part in parts if "=" in part)
	seen: set[str] = set()
	kept: list[str] = []
	for part in parts:
		simplified: str | None = simplify_attribute(part, counts, seen)
		if simplified is not None:
			kept.append(simplified)
	return selector[:start + 1] + ",".join(kept) + selector[end:]


def simplify_attribute(part: str, counts: Counter[str], seen: set[str]) -> str | None:
	""" One selector attribute as shown, None for a repeat of an attribute already shown, which `seen` records. """
	if "=" not in part:
		return part
	name: str = part.split("=")[0]
	negated: bool = part.startswith(name + "=!")
	if name == "nbt":
		if len(part.split("=", 1)[1]) <= 50:
			return part
		return "nbt=!{...}" if negated else "nbt={...}"
	if counts[name] == 1:
		return part
	if name in seen:
		return None
	seen.add(name)
	if name not in SIMPLIFIED_ATTRIBUTES:
		return part
	return f"{name}=!..." if negated else f"{name}=..."


__test__: dict[str, str] = {
	"parse_execution_context_from_line": """
	>>> None is parse_execution_context_from_line("say hello")
	True
	>>> parse_execution_context_from_line("execute as @s run function test:func")
	'as @s'
	>>> parse_execution_context_from_line("execute as @e[type=zombie] run function test:func")
	'as @e[type=zombie]'
	>>> parse_execution_context_from_line("execute in minecraft:overworld run function test:func")
	'in minecraft:overworld'
	>>> parse_execution_context_from_line("execute positioned 0 64 0 run function test:func")
	'positioned 0 64 0'
	>>> parse_execution_context_from_line("execute rotated 90 0 run function test:func")
	'rotated 90 0'
	>>> parse_execution_context_from_line("execute facing entity @s feet run function test:func")
	'facing entity @s feet'
	""",
}

