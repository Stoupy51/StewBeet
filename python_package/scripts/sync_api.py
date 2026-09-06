""" Regenerate the mechanical parts of the package layout: re-export lists and lazy import markers.

Explicit re-exports are what makes PEP 810 lazy imports work, since a star import resolves every
deferred name at once. Maintaining those lists by hand is the price, so this script derives them
from the source instead: add a function to a module, run this, and the parent packages follow.

Run ``python scripts/sync_api.py`` to rewrite the tree, or ``--check`` to fail without writing,
which is what CI uses.
"""
# Imports
import ast
import importlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

# Constants
ROOT: Path = Path(__file__).resolve().parent.parent / "stewbeet"
""" Root of the package this script maintains. """

MARKER_HEADER: str = "# Lazy imports (PEP 810), ignored before Python 3.15"
""" Comment introducing the __lazy_modules__ declaration. """

MARKER: tuple[str, ...] = (MARKER_HEADER, "from stouputils.lazy import ALWAYS_LAZY", "", "__lazy_modules__ = ALWAYS_LAZY")
""" The declaration inserted at the top of every module, kept to two statements so isort leaves it alone. """

MARKER_PATTERN: re.Pattern[str] = re.compile(
	rf"{re.escape(MARKER_HEADER)}\nfrom stouputils.lazy import ALWAYS_LAZY\n\n__lazy_modules__ = ALWAYS_LAZY\n\n"
)
""" The generated declaration, matched whole so a partial strip can never leave a duplicate behind. """

EXTERNAL_CACHE: dict[str, "Module | None"] = {}
""" Modules parsed from other distributions, keyed by name, since several packages re-export the same ones. """

INTERNAL: tuple[str, ...] = (
	"stewbeet.all",
	"stewbeet.cli",
	"stewbeet.contrib",
	"stewbeet.continuous_delivery",
	"stewbeet.core.dump",
	"stewbeet.core.migrate",
	"stewbeet.core.template",
	"stewbeet.dependencies",
	"stewbeet.plugins",
	"stewbeet.silent",
	"stewbeet.telemetry",
	"stewbeet.utils",
)
""" Subtrees addressed by their own import path, so they are not expected in the flat namespace.

The three stewbeet.core entries back a CLI subcommand each, dispatched by name from cli.py.
"""


# Classes
@dataclass
class Module:
	""" One source file, described well enough to regenerate the parts this script owns. """
	fqn: str
	""" Fully qualified module name, ex: "stewbeet.core.cls.recipe". """
	path: Path
	""" Source file path. """
	is_package: bool
	""" Whether the file is an __init__.py. """
	defined: list[str] = field(default_factory=list[str])
	""" Public names defined at top level, in source order. """
	explicit_all: list[str] | None = None
	""" Contents of __all__ when the module declares one, which then wins over everything else. """
	reexports: dict[str, tuple[int, int]] = field(default_factory=dict[str, tuple[int, int]])
	""" Re-exported module mapped to the line range of its import statement, 0-indexed and half open. """
	selective: list[str] = field(default_factory=list[str])
	""" Names re-exported one at a time by hand, which this script reads but never rewrites. """

	@property
	def package(self) -> str:
		""" Name of the package this module lives in. """
		return self.fqn if self.is_package else self.fqn.rsplit(".", 1)[0]


class Analyzer:
	""" Static reader of the package, importing only the third party modules it has to enumerate. """

	@staticmethod
	def fqn_of(path: Path) -> str:
		""" Convert a source path to its fully qualified module name. """
		parts: list[str] = list(path.relative_to(ROOT.parent).parts)
		parts[-1] = parts[-1].removesuffix(".py")
		if parts[-1] == "__init__":
			parts.pop()
		return ".".join(parts)

	@staticmethod
	def resolve(module: Module, level: int, name: str | None) -> str:
		""" Resolve a relative import against the module doing the importing. """
		parts: list[str] = module.package.split(".")
		base: list[str] = parts[: len(parts) - (level - 1)] if level > 1 else parts
		return ".".join([*base, name] if name else base)

	@staticmethod
	def defined_by(node: ast.stmt) -> list[str]:
		""" Return the public names a top level statement binds. """
		match node:
			case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
				return [node.name] if not node.name.startswith("_") else []
			case ast.TypeAlias():
				return [node.name.id] if not node.name.id.startswith("_") else []
			case ast.Assign():
				return [t.id for t in node.targets if isinstance(t, ast.Name) and not t.id.startswith("_")]
			case ast.AnnAssign():
				target: ast.expr = node.target
				return [target.id] if isinstance(target, ast.Name) and not target.id.startswith("_") else []
			case _:
				return []

	@staticmethod
	def read(path: Path, fqn: str = "") -> Module:
		""" Parse one source file, naming it explicitly when it lives outside the package. """
		module: Module = Module(fqn=fqn or Analyzer.fqn_of(path), path=path, is_package=path.name == "__init__.py")
		tree: ast.Module = ast.parse(path.read_text(encoding="utf-8").replace("\r\n", "\n"))
		for node in tree.body:
			module.defined.extend(n for n in Analyzer.defined_by(node) if n not in module.defined)
			if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
				if any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
					module.explicit_all = [
						element.value for element in node.value.elts
						if isinstance(element, ast.Constant) and isinstance(element.value, str)
					]
			if isinstance(node, ast.ImportFrom):
				target: str = Analyzer.resolve(module, node.level, node.module) if node.level else (node.module or "")
				end: int = node.end_lineno or node.lineno
				# A star import, or a parenthesized block whose every name uses the redundant
				# "name as name" form. A one line "from .x import y as y" stays a selective import.
				star: bool = any(alias.name == "*" for alias in node.names)
				full: bool = end > node.lineno and all(alias.asname == alias.name for alias in node.names)
				if star or full:
					module.reexports[target] = (node.lineno - 1, end)
				elif end == node.lineno:
					module.selective.extend(a.name for a in node.names if a.asname == a.name)
		return module

	@staticmethod
	def read_all() -> dict[str, Module]:
		""" Parse every source file in the package. """
		return {
			Analyzer.fqn_of(path): Analyzer.read(path)
			for path in sorted(ROOT.rglob("*.py")) if "__pycache__" not in path.parts
		}

	@staticmethod
	def external(fqn: str) -> Module | None:
		""" Parse a module from another distribution, so its exports read like a local one's.

		Returns None for anything without Python source to read, such as a C extension, leaving
		the caller to fall back on the interpreter.
		"""
		if fqn in EXTERNAL_CACHE:
			return EXTERNAL_CACHE[fqn]
		try:
			spec: importlib.machinery.ModuleSpec | None = importlib.util.find_spec(fqn)
		except (ImportError, AttributeError, ValueError):
			spec = None
		found: Module | None = None
		if spec is not None and spec.origin and spec.origin.endswith(".py"):
			found = Analyzer.read(Path(spec.origin), fqn=fqn)
		EXTERNAL_CACHE[fqn] = found
		return found

	@staticmethod
	def runtime_exports(fqn: str) -> list[str]:
		""" Last resort for a module with no readable source: ask the interpreter what it holds.

		Submodules are dropped on purpose. Binding one under this package's namespace shadows the
		package's own submodule of that name, and PEP 810 turns that shadowing into a hard failure.
		"""
		module: ModuleType = importlib.import_module(fqn)
		declared: object = getattr(module, "__all__", None)
		names: list[str] = (
			[name for name in declared if isinstance(name, str)] if isinstance(declared, list | tuple)
			else [name for name in vars(module) if not name.startswith("_")]
		)
		return sorted(name for name in names if not isinstance(getattr(module, name, None), ModuleType))

	@staticmethod
	def exports_of(fqn: str, modules: dict[str, Module], seen: frozenset[str] = frozenset()) -> list[str]:
		""" Return every public name a module exposes, following its own re-exports. """
		module: Module | None = modules.get(fqn)
		if module is None:
			if fqn == ROOT.name or fqn.startswith(f"{ROOT.name}."):
				raise SystemExit(f"{fqn} has no __init__.py, so re-exporting from it would import nothing")
			# Read the other distribution's source so its plain imports stay out of our namespace:
			# pyright refuses to treat those as exports, and re-advertising them would fail strict mode.
			module = Analyzer.external(fqn)
			if module is None:
				return Analyzer.runtime_exports(fqn)
		if fqn in seen:
			return []
		if module.explicit_all is not None:
			return sorted(module.explicit_all)
		names: set[str] = set(module.defined) | set(module.selective)
		for target in module.reexports:
			names.update(Analyzer.exports_of(target, modules, seen | {fqn}))
		return sorted(names)


class Renderer:
	""" Builder of the two blocks this script owns. """

	@staticmethod
	def sort_key(name: str) -> tuple[int, str]:
		""" Order names the way ruff's isort does, constants first, then classes, then the rest. """
		if name.isupper():
			return (0, name.lower())
		return (1 if name[:1].isupper() else 2, name.lower())

	@staticmethod
	def relative(target: str, package: str) -> str:
		""" Render an import target as ruff would sort it, relative for anything inside the package.

		Examples:
			>>> Renderer.relative("stewbeet.core.constants", "stewbeet.core")
			'.constants'
			>>> Renderer.relative("stewbeet.core.constants", "stewbeet.core.definitions_helper")
			'..constants'
			>>> Renderer.relative("beet", "stewbeet")
			'beet'
		"""
		if not target.startswith(f"{ROOT.name}."):
			return target
		if target.startswith(f"{package}."):
			return "." + target.removeprefix(f"{package}.")
		here: list[str] = package.split(".")
		there: list[str] = target.split(".")
		shared: int = 0
		while shared < min(len(here), len(there)) and here[shared] == there[shared]:
			shared += 1
		return "." * (len(here) - shared + 1) + ".".join(there[shared:])

	@staticmethod
	def reexport(target: str, package: str, names: list[str], trailing: str) -> list[str]:
		""" Render one explicit re-export statement, in the redundant alias form pyright requires. """
		body: list[str] = [f"\t{name} as {name}," for name in sorted(names, key=Renderer.sort_key)]
		return [f"from {Renderer.relative(target, package)} import (", *body, f"){trailing}"]

	@staticmethod
	def insertion_point(lines: list[str], tree: ast.Module) -> tuple[int, int, list[str]]:
		""" Find where the marker belongs and how to space it: after any docstring and any __future__ import.

		A __future__ import has to come first, so the marker slots in just below it and the blank
		lines that followed are re-emitted underneath. Keeping their count is what stops the marker
		from turning two blank lines before a class into one, which pycodestyle would then reject.
		"""
		point: int = 0
		first: ast.stmt = tree.body[0]
		if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
			point = first.end_lineno or 1
		futures: list[int] = [
			node.end_lineno or node.lineno for node in tree.body
			if isinstance(node, ast.ImportFrom) and node.module == "__future__"
		]
		if not futures:
			if any(line.strip() == "# Imports" for line in lines[point:]):
				point = next(index for index in range(point, len(lines)) if lines[index].strip() == "# Imports")
			else:
				while point < len(lines) and not lines[point].strip():
					point += 1
			return point, point, [*MARKER, ""]

		start: int = max(point, max(futures))
		end: int = start
		while end < len(lines) and not lines[end].strip():
			end += 1
		return start, end, ["", *MARKER, *[""] * max(end - start, 1)]


class Syncer:
	""" Rewriter keeping every generated block in step with the source. """

	@staticmethod
	def strip_marker(text: str, fqn: str) -> str:
		""" Drop a previously generated marker block, matching it whole so nothing is left behind. """
		stripped: str = MARKER_PATTERN.sub("", text)
		if "__lazy_modules__" in stripped:
			raise SystemExit(f"{fqn} declares __lazy_modules__ by hand, remove it and let this script own it")
		return stripped

	@staticmethod
	def sync(module: Module, modules: dict[str, Module]) -> str | None:
		""" Produce the new source for one module, or None when nothing needs to change. """
		original: str = module.path.read_text(encoding="utf-8", newline="")
		newline: str = "\r\n" if "\r\n" in original else "\n"
		lines: list[str] = original.replace("\r\n", "\n").split("\n")

		# Two targets can export the same name, so the one isort sorts last keeps it, which is the
		# module a star import used to leave standing. Third party blocks sort before local ones.
		owner: dict[str, str] = {}
		for target in sorted(module.reexports, key=lambda name: (name.startswith(f"{ROOT.name}."), name)):
			owner.update(dict.fromkeys(Analyzer.exports_of(target, modules), target))

		# Refresh the blocks from the bottom up, so the earlier line numbers stay valid
		for target, (start, end) in sorted(module.reexports.items(), key=lambda item: item[1], reverse=True):
			comment: re.Match[str] | None = re.search(r"\s*#.*$", lines[end - 1])
			trailing: str = comment.group(0) if comment else ""
			names: list[str] = [name for name, holder in owner.items() if holder == target]
			if not names:
				raise SystemExit(f"{module.fqn} re-exports {target}, which leaves it no name to bind, drop the import")
			lines[start:end] = Renderer.reexport(target, module.package, names, trailing)

		lines = Syncer.strip_marker("\n".join(lines), module.fqn).split("\n")
		start, end, block = Renderer.insertion_point(lines, ast.parse("\n".join(lines)))
		lines[start:end] = block

		updated: str = "\n".join(lines).replace("\n", newline)
		return updated if updated != original else None

	@staticmethod
	def collisions(modules: dict[str, Module]) -> list[str]:
		""" Report submodules whose name shadows a name their own package binds.

		Such a module cannot be deferred: the import system overwrites the unresolved binding with
		the module object, so the package ends up exposing a module where a function is expected.
		"""
		problems: list[str] = []
		for fqn, module in modules.items():
			children: set[str] = {other.rsplit(".", 1)[-1] for other in modules if other.rsplit(".", 1)[0] == fqn}
			# A name the package binds to the submodule itself is the same object either way
			shadowed: set[str] = children & set(Analyzer.exports_of(fqn, modules)) & set(module.defined)
			problems.extend(f"{fqn}.{name} is both a submodule and an exported name, rename the module" for name in sorted(shadowed))
		return problems

	@staticmethod
	def unexported(modules: dict[str, Module]) -> list[str]:
		""" Report modules no package re-exports, so a new one is not silently left out of the API.

		Packages driving their exports through __all__ manage their own children, and the subtrees
		listed in INTERNAL are reached through their own import path rather than the flat namespace.
		"""
		reexported: set[str] = {target for module in modules.values() for target in module.reexports}
		forgotten: list[str] = []
		for fqn, module in sorted(modules.items()):
			parent: Module | None = modules.get(fqn.rsplit(".", 1)[0])
			if fqn in reexported or fqn == ROOT.name or not module.defined:
				continue
			if any(fqn == name or fqn.startswith(f"{name}.") for name in INTERNAL):
				continue
			if parent is None or parent.explicit_all is not None:
				continue
			forgotten.append(fqn)
		return forgotten


# Functions
def main() -> int:
	""" Sync the tree, or check it, depending on the command line. """
	check_only: bool = "--check" in sys.argv
	modules: dict[str, Module] = Analyzer.read_all()

	problems: list[str] = Syncer.collisions(modules)
	for problem in problems:
		print(f"error: {problem}")

	changed: list[str] = []
	for fqn, module in modules.items():
		updated: str | None = Syncer.sync(module, modules)
		if updated is not None:
			changed.append(fqn)
			if not check_only:
				module.path.write_text(updated, encoding="utf-8", newline="")

	for fqn in Syncer.unexported(modules):
		print(f"note: {fqn} is not re-exported by any package, add it by hand if that is wrong")

	if check_only and changed:
		print(f"\nerror: {len(changed)} modules are out of sync, run: python scripts/sync_api.py")
		for fqn in changed:
			print(f"    {fqn}")
	elif changed:
		print(f"\n{len(changed)} modules updated")
	else:
		print("\nalready in sync")
	return 1 if problems or (check_only and changed) else 0


if __name__ == "__main__":
	raise SystemExit(main())
