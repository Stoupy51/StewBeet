""" Probe: can a command in a mecha AST be attributed to the module that wrote it?

Listed before `mecha` in the pipeline and doing its work after the yield, so it runs once mecha has
compiled and while the `Module` compilation units are still in the database.
"""

# Imports
import json
import os
from collections.abc import Iterator
from typing import Any

from beet import Context
from mecha import AstCommand, Mecha


# Functions
def sits_at(source: str, pos: int, lineno: int, colno: int) -> bool:
	""" Whether offset `pos` of `source` is at 1-based line `lineno`, column `colno`.

	The three fields of a `SourceLocation` are mutually redundant, so a file that did not produce
	the node almost always disagrees with at least one of them.

	>>> sits_at("ab\\ncd\\n", 3, 2, 1), sits_at("ab\\ncd\\n", 3, 1, 4)
	(True, False)
	"""
	if pos > len(source):
		return False
	before: str = source[:pos]
	return before.count("\n") + 1 == lineno and pos - before.rfind("\n") == colno


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
	yield
	mc: Mecha = ctx.inject(Mecha)
	sources: dict[str, str] = {
		unit.filename: unit.source
		for unit in mc.database.values()
		if unit.filename and unit.source
	}

	result: dict[str, Any] = {"sources": sorted(sources), "functions": {}}
	for path, func in ctx.data.functions.items():
		unit = mc.database.get(func)
		if unit is None or unit.ast is None:
			continue
		result["functions"][path] = {
			"unit_filename": unit.filename,
			"text": func.text,
			"commands": [
				{
					"index": index,
					"identifier": command.identifier if isinstance(command, AstCommand) else None,
					"pos": command.location.pos,
					"lineno": command.location.lineno,
					"colno": command.location.colno,
					"owners": [name for name, text in sources.items() if sits_at(text, command.location.pos, command.location.lineno, command.location.colno)],
				}
				for index, command in enumerate(unit.ast.commands)
			],
		}

	out: str = os.environ.get("BOLT_PROBE_OUT", "result.json")
	with open(out, "w", encoding="utf-8") as file:
		json.dump(result, file, indent=2)
	print(f"probe: wrote {out}")

