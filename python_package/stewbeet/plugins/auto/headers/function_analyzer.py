"""
Function relationship analysis for Minecraft datapack headers.

This module handles building the relationships between functions, tags,
advancements, and function calls to create the @within information.
"""

# pyright: reportUnnecessaryIsInstance=false
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import re
from typing import cast

from beet import Context

from .execution_parser import parse_execution_context_from_line
from .object import Header

FUNCTION_CALL_RE = re.compile(r"function\s+([#]?[\w./-]+:[\w./-]+)")

COMMAND_CALL_RE = re.compile(
	r"(?:^\s*\$?\s*|\brun\s+|(?P<sched>\bschedule\s+))function\s+([#]?[\w./-]+:(?:[\w./-]|\$\(\w+\))+)"
)
""" A *command* call to a function, the "function" keyword sitting at the start of the command or right after "run " or "schedule ".

A "$" macro prefix may come first, and the path may hold macro placeholders ($function ns:types/$(type)), never the namespace.
References inside an argument string, like a tellraw suggest_command "/function ns:foo", are left out:
their trailing JSON must never be mistaken for a macro ({...}) or a schedule time (100t).
Since "run " also appears inside quoted dialog commands (`command:"/execute ... run function ns:foo"`),
a match is only a real command when it is not inside a string, see :meth:`FunctionAnalyzer.is_inside_string`.
"""

QUOTED_ID_RE = re.compile(r"""\w*function\w*["']?\s*:\s*(["'])([\w.-]+:[\w./-]+)\1""")
""" A quoted function id under a key naming a function ({give_function:"ns:x"}, "function": "ns:x").

It is handed to a macro running "$function $(id)" or to a run_function effect.
Other keys are left out, since a dialog id can equal a function id.
"""

PLACEHOLDER_RE = re.compile(r"\$\(\w+\)")


# Class
class FunctionAnalyzer:
	""" Analyzes function relationships and builds @within information. """

	def __init__(self, ctx: Context, mcfunctions: dict[str, Header]):
		""" Initialize the function analyzer.

		Args:
			ctx:         The beet context
			mcfunctions: Dictionary mapping function paths to Header objects
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
					function_path_str: str = cast(dict[str,str],function_path).get("id", "")
					if function_path_str in self.mcfunctions:
						self.mcfunctions[function_path_str].within.append(to_be_called)

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

	def analyze_dialogs(self) -> None:
		""" Record the functions dialog buttons call, which would otherwise look like orphans (``@within ???``).

		Commands are found in the serialized ``.text``, wherever the dialog schema puts them.
		Reading ``.data`` would deserialize the file, re-encoding it on output and losing its formatting.

		>>> from types import SimpleNamespace
		>>> dialog = SimpleNamespace(
		...     text='{"actions":[{"action":{"type":"run_command","command":"/function test:menu"}}]}'
		... )
		>>> ctx = SimpleNamespace(data=SimpleNamespace(dialogs={"test:config": dialog}))
		>>> menu = Header("test:menu", [], [], "")
		>>> FunctionAnalyzer(ctx, {"test:menu": menu}).analyze_dialogs()  # type: ignore[arg-type]
		>>> menu.within
		['dialog test:config']
		"""
		for dialog_path, dialog in self.ctx.data.dialogs.items():
			# Mirrors the "advancement <path>" convention used by analyze_advancements
			self.add_text_references(f"dialog {dialog_path}", dialog.text)

	def analyze_enchantments(self) -> None:
		""" Analyze enchantments, whose ``run_function`` effects name a function as a plain JSON string.

		Scanned as serialized text for the same reason as :meth:`analyze_dialogs`.

		>>> from types import SimpleNamespace
		>>> enchantment = SimpleNamespace(
		...     text='{"effects":{"minecraft:tick":[{"effect":{"type":"run_function","function":"test:on_tick"}}]}}'
		... )
		>>> ctx = SimpleNamespace(data=SimpleNamespace(enchantments={"test:magic": enchantment}))
		>>> on_tick = Header("test:on_tick", [], [], "")
		>>> FunctionAnalyzer(ctx, {"test:on_tick": on_tick}).analyze_enchantments()  # type: ignore[arg-type]
		>>> on_tick.within
		['enchantment test:magic']
		"""
		for enchantment_path, enchantment in self.ctx.data.enchantments.items():
			self.add_text_references(f"enchantment {enchantment_path}", enchantment.text)

	def add_text_references(self, caller: str, text: str) -> None:
		""" Record ``caller`` on every function that ``text`` names, as a command or as a quoted id.

		Args:
			caller: The @within entry to add.
			text:   The serialized file to scan.
		"""
		found: list[str] = [match.group(1) for match in FUNCTION_CALL_RE.finditer(text)]
		found += [match.group(2) for match in QUOTED_ID_RE.finditer(text)]
		for called in found:
			if called in self.mcfunctions and caller not in self.mcfunctions[called].within:
				self.mcfunctions[called].within.append(caller)

	def analyze_function_calls(self) -> None:
		""" Record in the header of every called function which function calls it, with the macro payload it passes.

		A reference inside an argument string, like a tellraw suggest_command, is a "string in <caller>",
		keeping the payload written right after it. A placeholder in the called path stands for every function it can match.

		>>> caller = Header("test:caller", [], [], '$function test:target {slot:"$(slot)"}')
		>>> mcfunctions = {"test:caller": caller, "test:target": Header("test:target", [], [], "")}
		>>> FunctionAnalyzer(None, mcfunctions).analyze_function_calls()  # type: ignore[arg-type]
		>>> mcfunctions["test:target"].within
		['test:caller {slot:"$(slot)"}']
		"""
		# For each mcfunction file, look at each line
		for path, header in self.mcfunctions.items():
			for line in header.content.split("\n"):

				# A quoted id is data the line hands over, so the function runs from elsewhere: a string reference
				for match in QUOTED_ID_RE.finditer(line):
					quoted: str = match.group(2)
					if quoted in self.mcfunctions and f"string in {path}" not in self.mcfunctions[quoted].within:
						self.mcfunctions[quoted].within.append(f"string in {path}")

				# Skip lines with no function reference at all
				if "function " not in line:
					continue

				# A real command call anchors "function" at the command start or after run/schedule, outside quoted arguments.
				# Its payload (macros, schedule time) and execution context only apply to that call.
				command_match = next(
					(m for m in COMMAND_CALL_RE.finditer(line) if not self.is_inside_string(line, m.start())),
					None,
				)
				if command_match is not None:
					primary: str = command_match.group(2)

					# Everything after the called function is macro data ({...}) or a schedule time
					more_text: str = line[command_match.end():].replace("\n", "").strip()
					more: str = f" {more_text}" if more_text else ""

					# "schedule function ..." loses execution context (it runs on a later tick)
					is_scheduled: bool = command_match.group("sched") is not None
					line_context: str | None = None if is_scheduled else parse_execution_context_from_line(line)

					# Create the caller string with context if available
					caller_info: str = path + more
					if line_context:
						line_context = "".join(
							x for i, x in enumerate(line_context)
							if x != " " or (i > 0 and line_context[i - 1] not in ":,")
						)
						caller_info += f" [ {line_context} ]"
					elif is_scheduled:
						# Mark scheduled calls with a special marker so context analyzer knows not to inherit context
						caller_info += " [ scheduled ]"

					# The primary call plus any nested references inside its macro payload (e.g.
					# function #tag:run {with: {on_exit_point: "function ns:path"}}) share this caller info.
					called_functions: list[str] = self.resolve_call(primary)
					for match in FUNCTION_CALL_RE.finditer(line):
						candidate: str = match.group(1)
						if candidate not in called_functions:
							called_functions.append(candidate)
					for called in called_functions:
						if called in self.mcfunctions and caller_info not in self.mcfunctions[called].within:
							self.mcfunctions[called].within.append(caller_info)

				# A reference inside an argument string is a "string in <caller>", whose clicked command runs as the player.
				# A macro payload after it is kept, since a "## /function ns:foo {x:1}" line may be the only typed example.
				else:
					for match in FUNCTION_CALL_RE.finditer(line):
						candidate = match.group(1)
						if candidate not in self.mcfunctions:
							continue
						payload: str = self.extract_macro_payload(line, match.end())
						caller_ref: str = f"string in {path}" + (f" {payload}" if payload else "")
						if caller_ref not in self.mcfunctions[candidate].within:
							self.mcfunctions[candidate].within.append(caller_ref)

	def analyze_all_relationships(self) -> None:
		""" Analyze all function relationships. """
		self.analyze_function_tags()
		self.analyze_advancements()
		self.analyze_function_calls()
		self.analyze_dialogs()  # Last: ContextAnalyzer takes the FIRST caller, so mcfunction callers keep priority
		self.analyze_enchantments()
		self.mark_public_functions(self.ctx.project_id, self.ctx.project_version)

	def resolve_call(self, called: str) -> list[str]:
		""" Return the functions a call can reach: the id itself, or every id its placeholders can match.

		Args:
			called: The called id, possibly holding ``$(name)`` placeholders.

		>>> headers = {path: Header(path) for path in ("t:a/x", "t:a/y/z", "t:b")}
		>>> analyzer = FunctionAnalyzer(None, headers)  # type: ignore[arg-type]
		>>> analyzer.resolve_call("t:a/$(id)")
		['t:a/x', 't:a/y/z']
		>>> analyzer.resolve_call("t:b")
		['t:b']
		"""
		if "$(" not in called:
			return [called]
		literals: list[str] = [re.escape(part) for part in PLACEHOLDER_RE.split(called)]
		pattern: re.Pattern[str] = re.compile(r"[\w./-]*".join(literals))
		return [path for path in self.mcfunctions if pattern.fullmatch(path)]

	def mark_public_functions(self, namespace: str, version: str) -> None:
		""" Mark the uncalled functions of the project outside its versioned folder as ``(public)``.

		Those are run by hand or by other packs (``ns:config``, ``ns:_give_all``), so ``???`` stays for dead code.
		Projects without a ``ns:v<version>/`` folder are left alone: nothing tells their API apart.

		Args:
			namespace: The project namespace.
			version:   The project version.

		>>> headers = {"t:config": Header("t:config"), "t:v1.0/dead": Header("t:v1.0/dead"), "other:x": Header("other:x")}
		>>> FunctionAnalyzer(None, headers).mark_public_functions("t", "1.0")  # type: ignore[arg-type]
		>>> [header.within for header in headers.values()]
		[['(public)'], [], []]
		"""
		versioned: str = f"{namespace}:v{version}/"
		if not version or not any(path.startswith(versioned) for path in self.mcfunctions):
			return
		for path, header in self.mcfunctions.items():
			if not header.within and path.startswith(f"{namespace}:") and not path.startswith(versioned):
				header.within.append("(public)")

	@staticmethod
	def extract_macro_payload(line: str, pos: int) -> str:
		""" Return the balanced ``{...}`` compound following the function reference that ends at ``pos``, or "" if there is none.

		Only a compound right after the reference counts as macro data,
		so the JSON surrounding a ``suggest_command`` reference, which closes with a quote and ``}}]``, yields an empty string.
		>>> FunctionAnalyzer.extract_macro_payload('## /function ns:foo {x:-280,is_auto:1}', 19)
		'{x:-280,is_auto:1}'
		>>> FunctionAnalyzer.extract_macro_payload('function ns:foo {with:{a:1}}', 15)
		'{with:{a:1}}'
		>>> FunctionAnalyzer.extract_macro_payload('{"command":"/function ns:foo"}]', 27)
		''
		"""
		rest: str = line[pos:].lstrip()
		if not rest.startswith("{"):
			return ""

		depth: int = 0
		for i, char in enumerate(rest):
			if char == "{":
				depth += 1
			elif char == "}":
				depth -= 1
				if depth == 0:
					return rest[:i + 1]
		return ""

	@staticmethod
	def is_inside_string(line: str, pos: int) -> bool:
		""" Return whether character index ``pos`` in ``line`` sits inside a double-quoted string.

		Counts unescaped double quotes before ``pos``; an odd count means an unclosed string is open.

		Args:
			line: The line to scan.
			pos:  The character index whose string-membership is tested.

		>>> FunctionAnalyzer.is_inside_string('run function a:b', 4)
		False
		>>> FunctionAnalyzer.is_inside_string('command:"/execute run function a:b"', 26)
		True
		>>> FunctionAnalyzer.is_inside_string('data set value {a:"x"} run function a:b', 30)
		False
		"""
		# Without a single backslash there is nothing to escape, so counting quotes is exact
		prefix: str = line[:pos]
		if "\\" not in prefix:
			return prefix.count('"') % 2 == 1

		quotes: int = 0
		i: int = 0
		while i < pos and i < len(line):
			char: str = line[i]
			if char == "\\":
				i += 2  # Skip the escaped character
				continue
			if char == '"':
				quotes += 1
			i += 1
		return quotes % 2 == 1


__test__: dict[str, str] = {
	"FunctionAnalyzer.analyze_dialogs": """
	>>> from types import SimpleNamespace
	>>> dialog = SimpleNamespace(text='{"type":"minecraft:notice","title":"hi"}')
	>>> ctx = SimpleNamespace(data=SimpleNamespace(dialogs={"test:notice": dialog}))
	>>> menu = Header("test:menu", [], [], "")
	>>> FunctionAnalyzer(ctx, {"test:menu": menu}).analyze_dialogs()  # type: ignore[arg-type]
	>>> menu.within
	[]
	>>> dialog = SimpleNamespace(text='["/function test:menu", "/function test:menu"]')
	>>> ctx = SimpleNamespace(data=SimpleNamespace(dialogs={"test:config": dialog}))
	>>> menu = Header("test:menu", [], [], "")
	>>> FunctionAnalyzer(ctx, {"test:menu": menu}).analyze_dialogs()  # type: ignore[arg-type]
	>>> menu.within
	['dialog test:config']
	""",
	"FunctionAnalyzer.analyze_function_calls": """
	>>> caller = Header(
	...     "test:caller",
	...     [],
	...     [],
	...     'function #bs.raycast:run {with: {on_exit_point: "function test:earth/on_exit"}}',
	... )
	>>> raycast = Header("#bs.raycast:run", [], [], "")
	>>> exit_fn = Header("test:earth/on_exit", [], [], "")
	>>> mcfunctions = {
	...     "test:caller": caller,
	...     "#bs.raycast:run": raycast,
	...     "test:earth/on_exit": exit_fn,
	... }
	>>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
	>>> analyzer.analyze_function_calls()
	>>> any(item.startswith("test:caller") for item in mcfunctions["test:earth/on_exit"].within)
	True
	>>> caller = Header(
	...     "test:menu",
	...     [],
	...     [],
	...     'tellraw @a [{"text":"[Restart]","click_event":{"action":"suggest_command","command":"/function test:restart"}}]',
	... )
	>>> restart = Header("test:restart", [], [], "")
	>>> mcfunctions = {"test:menu": caller, "test:restart": restart}
	>>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
	>>> analyzer.analyze_function_calls()
	>>> mcfunctions["test:restart"].within
	['string in test:menu']
	>>> caller = Header("test:caller", [], [], '$function test:target {slot:"$(slot)"}')
	>>> target = Header("test:target", [], [], "")
	>>> mcfunctions = {"test:caller": caller, "test:target": target}
	>>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
	>>> analyzer.analyze_function_calls()
	>>> mcfunctions["test:target"].within
	['test:caller {slot:"$(slot)"}']
	>>> place = Header("test:place", [], [], '## /function test:place {x:-280,duration:80}\\n$say $(x) $(duration)')
	>>> mcfunctions = {"test:place": place}
	>>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
	>>> analyzer.analyze_function_calls()
	>>> mcfunctions["test:place"].within
	['string in test:place {x:-280,duration:80}']
	>>> caller = Header("test:apply", [], [], '$function test:perks/$(perk) {level:1}')
	>>> mcfunctions = {"test:apply": caller, "test:perks/a": Header("test:perks/a"), "test:perks/b": Header("test:perks/b")}
	>>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
	>>> analyzer.analyze_function_calls()
	>>> mcfunctions["test:perks/a"].within, mcfunctions["test:perks/b"].within
	(['test:apply {level:1}'], ['test:apply {level:1}'])
	>>> body = 'function test:give_via {give_function:"test:give/weapon",back:{dialog:"test:give_via"}}'
	>>> mcfunctions = {"test:box": Header("test:box", content=body)}
	>>> mcfunctions |= {path: Header(path) for path in ("test:give_via", "test:give/weapon")}
	>>> analyzer = FunctionAnalyzer(None, mcfunctions)  # type: ignore[arg-type]
	>>> analyzer.analyze_function_calls()
	>>> mcfunctions["test:give/weapon"].within
	['string in test:box']
	>>> mcfunctions["test:give_via"].within
	['test:box {give_function:"test:give/weapon",back:{dialog:"test:give_via"}}']
	""",
}

