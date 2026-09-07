""" Which of the project's own `.mcfunction` sources no vanilla parser can read.

Two things take a source file out of vanilla mcfunction, and both are read off structures the build
already has rather than guessed from the text: bolt generated Python for it, or mecha split it into
more than one function.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from collections.abc import Callable

from beet import Context
from bolt import Runtime
from mecha import Mecha


# Functions
def unparseable_sources(ctx: Context) -> list[str]:
	""" Project-relative paths of the `.mcfunction` sources Spyglass reports as broken.

	Returns:
		Sorted forward-slash paths, the shape `env.exclude` patterns are matched against.
	"""
	mc: Mecha | None = existing_service(ctx, Mecha)
	if mc is None:
		return []
	found: set[str] = nested_sources(mc) | bolt_sources(ctx, mc)
	return sorted(name for name in found if name.endswith(".mcfunction"))


def nested_sources(mc: Mecha) -> set[str]:
	""" Files backing more than one compilation unit, which is mecha's `function ./name:` nesting.

	Nesting is not vanilla syntax twice over: the line opening a body ends in a colon, and `./name`
	is not a resource location. A file using it is a file Spyglass underlines.
	"""
	seen: set[str] = set()
	repeated: set[str] = set()
	for unit in mc.database.values():
		name: str | None = project_relative(unit.filename)
		if name is None:
			continue
		if name in seen:
			repeated.add(name)
		seen.add(name)
	return repeated


def bolt_sources(ctx: Context, mc: Mecha) -> set[str]:
	""" Files bolt generated Python for, which is every file that used bolt syntax.

	A plain function compiled while bolt is loaded keeps its `python` at None, so this says the file
	used bolt rather than that bolt was available.
	"""
	runtime: Runtime | None = existing_service(ctx, Runtime)
	if runtime is None:
		return set()

	found: set[str] = set()
	for file, module in runtime.modules.registry.items():
		if not module.python:
			continue
		unit = mc.database.get(file)
		name: str | None = project_relative(unit.filename if unit else None)
		if name is not None:
			found.add(name)
	return found


def existing_service[T](ctx: Context, service: Callable[[Context], T]) -> T | None:
	""" A service this build already has, or None when nothing asked for one.

	`ctx.inject` creates what it cannot find, and creating bolt's runtime at the end of a build
	would enable bolt on a project that does not use it, so the container is read instead.
	"""
	if not any(key is service for key in ctx._container): # pyright: ignore[reportPrivateUsage]
		return None
	return ctx.inject(service)


def project_relative(filename: str | None) -> str | None:
	""" A compiled file's path relative to the project root, or None when no pattern could name it.

	`CompilationUnit.filename` is already relative to beet's project directory, so this normalises
	separators and drops what an `env.exclude` entry cannot reach: Spyglass matches its patterns
	against paths relative to the root it indexes.

	>>> project_relative("src/data/ns/function/a.mcfunction")
	'src/data/ns/function/a.mcfunction'
	>>> project_relative("src\\\\data\\\\ns\\\\function\\\\a.mcfunction")
	'src/data/ns/function/a.mcfunction'
	>>> [project_relative(outside) for outside in ("../shared/x.mcfunction", "/tmp/x.mcfunction", "D:/x.mcfunction", None)]
	[None, None, None, None]
	"""
	if not filename:
		return None
	name: str = filename.replace("\\", "/")
	return None if name.startswith(("../", "/")) or ":" in name else name
