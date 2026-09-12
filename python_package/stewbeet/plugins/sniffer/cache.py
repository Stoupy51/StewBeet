""" Reuse of the previous build's sidecars, one function at a time.

Reconciling what was written against what the pack ended up holding is a `difflib` pass per function,
and it is where nearly all of this plugin's time goes. A map is a pure function of the recorded chunks,
the function's final text and where the pack is written, so a function whose inputs are all unchanged
gets its previous map back rather than being aligned again. The record is per function rather than per
pack, so editing one function costs one alignment.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import hashlib
import json
from collections.abc import Sequence

from beet import Cache

from .model import WriteChunk

# Constants
CACHE_NAME: str = "sniffer_maps"
""" Beet cache slot holding the sidecars of the previous build. """

CACHE_KEY: str = "maps"
""" Key of the file inside that slot, resolved through the cache so the path stays beet's business. """


# Functions
def map_signature(chunks: Sequence[WriteChunk], text: str, layout: str) -> str:
	""" Hash everything one function's map is built from.

	Args:
		text:   The function's final text, which the chunks are reconciled against.
		layout: Where the pack is written, since `sourceRoot` and every source are relative to it.

	>>> chunk = WriteChunk(lines=("say a",), origin=None)
	>>> map_signature([chunk], "say a\\n", "/p") == map_signature([chunk], "say a\\n", "/p")
	True
	>>> map_signature([chunk], "say a\\n", "/p") == map_signature([chunk], "say b\\n", "/p")
	False
	>>> map_signature([chunk], "say a\\n", "/p") == map_signature([chunk], "say a\\n", "/elsewhere")
	False
	"""
	digest = hashlib.sha1(layout.encode())
	for chunk in chunks:
		origin = chunk.origin
		source: str = "-" if origin is None else f"{origin.file}:{origin.line}:{origin.column}:{origin.exact:d}"
		digest.update(f"{source}\0{len(chunk.lines)}\0".encode())
		digest.update("\n".join(chunk.lines).encode())
	digest.update(b"\0")
	digest.update(text.encode())
	return digest.hexdigest()


def load_maps(cache: Cache) -> dict[str, tuple[str, str]]:
	""" The previous build's sidecars, keyed by function path, as its signature and its JSON.

	Anything at all wrong with the record reads as an empty one, which costs a rebuild of every map
	and nothing else.
	"""
	try:
		raw: dict[str, object] = json.loads(cache.get_path(CACHE_KEY).read_text("utf-8"))
		entries: list[tuple[str, object]] = list(raw.items())
	except (OSError, ValueError, AttributeError):
		return {}

	maps: dict[str, tuple[str, str]] = {}
	for path, entry in entries:
		match entry:
			case [str(signature), str(rendered)]:
				maps[path] = (signature, rendered)
			case _:
				continue
	return maps


def store_maps(cache: Cache, maps: dict[str, tuple[str, str]]) -> None:
	""" Record this build's sidecars so the next one can skip aligning what it did not change. """
	path = cache.get_path(CACHE_KEY)
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps({key: list(entry) for key, entry in maps.items()}), "utf-8")

