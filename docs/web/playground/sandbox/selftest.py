""" Run every job once at image build time, so a broken pipeline fails the image and not a visitor.

The render node is the playground case that matters. auto.text_renders reaches model_resolver, and
the OpenGL context this container has no display for, for any item with no cached render:
emit.source_images -> ensure_item_images -> run_model_resolver. src.placeholders is what keeps that
queue empty, and this is what notices the day it stops working.

The headers case is here for the same reason: it builds a two function pack and checks that the
archive that comes back has grown a header, which is the whole contract of the endpoint.
"""
# Imports
import io
from typing import Any
from zipfile import ZipFile

from builds import Build, Headers

# Constants
DEFINITIONS: str = (
	"from beet import Context\n"
	"from stewbeet import *\n"
	"\n"
	"\n"
	"def beet_default(ctx: Context):\n"
	'    Item(id="{item}", components={{"item_name": {{"text": "Selftest"}}{lore}}})\n'
	"    add_item_model_component()\n"
)
""" Every playground case is a definitions module, because that is the only shape the pipeline takes. """

RENDER_LORE: str = ', "lore": [[{"render": "steel_ingot"}]]'
""" The component that drags model_resolver into the build when the render cache is not seeded. """

PACK_MCMETA: str = '{"pack": {"pack_format": 61, "description": "selftest"}}'
""" Minimal pack.mcmeta for the uploaded pack, on a format that uses the `function` folder. """

CALLER: str = "function selftest:called\n"
""" Calls the other function, so the analysis has a @within relationship to find. """

CALLED: str = "say hello\n"
""" Called by the other one, and the file the header has to appear in. """


# Functions
def sample_pack() -> bytes:
	""" A two function datapack, zipped, as an upload would arrive.

	Returns:
		bytes: The archive.
	"""
	buffer: io.BytesIO = io.BytesIO()
	with ZipFile(buffer, "w") as archive:
		archive.writestr("pack.mcmeta", PACK_MCMETA)
		archive.writestr("data/selftest/function/caller.mcfunction", CALLER)
		archive.writestr("data/selftest/function/called.mcfunction", CALLED)
	return buffer.getvalue()


def check_builds() -> list[str]:
	""" Build each playground case once and report the ones that failed.

	Returns:
		list[str]: Failure lines, empty when every build succeeded.
	"""
	cases: dict[str, str] = {
		"bundled texture": DEFINITIONS.format(item="steel_ingot", lore=""),
		"no texture at all": DEFINITIONS.format(item="zzz_nothing_has_this_name", lore=""),
		"a render node": DEFINITIONS.format(item="steel_ingot", lore=RENDER_LORE),
	}
	failures: list[str] = []
	for name, code in cases.items():
		result: dict[str, Any] = Build.run(code)
		count: int = len(result.get("files", []))
		if result.get("ok") and count > 0:
			print(f"selftest: {name}: {count} files in {result.get('durationMs')} ms")
		else:
			failures.append(f"selftest: {name}: FAILED ({result.get('error')})\n{result.get('logs', '')[-4000:]}")
	return failures


def check_headers() -> list[str]:
	""" Run the headers job over a sample pack and check the archive that comes back.

	Returns:
		list[str]: Failure lines, empty when the pass did what it says it does.
	"""
	payload, archive = Headers.run(sample_pack())
	if not payload.get("ok"):
		return [f"selftest: headers: FAILED ({payload.get('error')})\n{payload.get('logs', '')[-4000:]}"]

	with ZipFile(io.BytesIO(archive)) as zipped:
		names: list[str] = zipped.namelist()
		called: str = zipped.read("data/selftest/function/called.mcfunction").decode("utf-8")

	failures: list[str] = []
	if "pack.mcmeta" not in names:
		failures.append(f"selftest: headers: pack.mcmeta missing from the archive, got {names}")
	# Naming the caller is what the whole endpoint exists to produce, and it can only be there if the
	# cross-referencing analysis ran, so one assertion covers both.
	if "@within" not in called or "selftest:caller" not in called:
		failures.append(f"selftest: headers: the caller was not found\n{called}")
	if not failures:
		print(f"selftest: headers: {payload.get('changed')}/{payload.get('functions')} functions in {payload.get('durationMs')} ms")
	return failures


def selftest() -> int:
	""" Run every case and report.

	Returns:
		int: 0 when everything passed.
	"""
	failures: list[str] = check_builds() + check_headers()
	for failure in failures:
		print(failure)
	return 1 if failures else 0

