""" Empty functions standing in, for Spyglass, for the ones whose source it was told to skip.

An excluded file declares nothing, so a plain `.mcfunction` calling the function it defines is told that function does not exist.
The build output declares it again when it keeps its name, but a versioning refactor that renames `ns:impl/load` into `ns:v1.2.3/load`
leaves the name the sources call declared nowhere. Each of those gets a one-line function in a pack of its own beside the build output,
which Spyglass indexes like any other pack in the workspace.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
import os
import re
import shutil

from beet import Context

# Constants
DIRECTORY: str = "spyglass_declarations"
""" The declaration pack's folder, inside the build output, rewritten by every build. """

FUNCTION_SOURCE: re.Pattern[str] = re.compile(r"(?:^|/)data/([^/]+)/functions?/(.+)\.mcfunction$")
""" A function source's namespace and path, from its project-relative path. """


# Functions
def write_declarations(ctx: Context, excluded: list[str]) -> int:
	""" Replace the declaration pack with one function per excluded source whose name the final pack lacks.

	Args:
		excluded: Project-relative paths of the sources Spyglass skips.
	Returns:
		How many functions it declares, 0 when the build has no output directory to put them in.
	"""
	if ctx.output_directory is None:
		return 0
	root: str = os.path.join(str(ctx.output_directory), DIRECTORY)
	shutil.rmtree(root, ignore_errors=True)
	missing: dict[str, str] = {
		name: source for source in excluded if (name := function_name(source)) is not None and name not in ctx.data.functions
	}
	if not missing:
		return 0

	os.makedirs(root)
	with open(os.path.join(root, "pack.mcmeta"), "w", encoding="utf-8") as file:
		json.dump(ctx.data.mcmeta.data, file, indent=4)
	for name, source in missing.items():
		namespace, path = name.split(":", 1)
		target: str = os.path.join(root, "data", namespace, "function", f"{path}.mcfunction")
		os.makedirs(os.path.dirname(target), exist_ok=True)
		with open(target, "w", encoding="utf-8") as file:
			file.write(f"# Declares {name} for Spyglass, which skips its source: {source}\n")
	return len(missing)


def function_name(source: str) -> str | None:
	""" The function a source file defines, from its project-relative path.

	>>> function_name("src/data/tns/function/impl/load.mcfunction"), function_name("load.mcfunction")
	('tns:impl/load', None)
	"""
	found: re.Match[str] | None = FUNCTION_SOURCE.search(source)
	return None if found is None else f"{found[1]}:{found[2]}"

