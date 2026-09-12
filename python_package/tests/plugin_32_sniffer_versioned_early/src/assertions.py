# Assertions for: maps that survive a versioning refactor moving every function before mecha parses it

# Imports
import json
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
EXPECTED: dict[str, str] = {
    # Compiled by mecha out of a .mcfunction holding bolt, mapped off the AST.
    "tns:v1.0.0/hello": "src/data/tns/function/impl/hello.mcfunction",
    "tns:v1.0.0/goodbye": "src/data/tns/function/impl/hello.mcfunction",
    # Written by a StewBeet helper, mapped from what the capture recorded under the old path.
    "tns:v1.0.0/written": "src/link.py",
}
""" Resource location, after the refactor, to the source file its map must name.
The two bolt ones are nested out of one file whose `source_path` the refactor threw away. """


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    yield

    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }

    # Without this the whole test passes on a build where nothing moved at all.
    moved: list[str] = [path for path in ctx.data.functions if path.startswith("tns:impl/")]
    assert not moved, f"the refactor should have moved every implementation function, {moved} stayed"

    for path, source in EXPECTED.items():
        assert path in ctx.data.functions, f"{path} was not written into the pack at all"

        map_path: str = f"data/{path.replace(':', '/function/', 1)}.mcfunction.map"
        assert map_path in maps, f"{path} has no map, so the refactor lost the origin of every line in it"
        sources: list[str] = [str(entry).replace("\\", "/") for entry in maps[map_path]["sources"]]
        assert sources == [source], f"{path} maps to {sources} rather than {source}"

    # A map is keyed by the function's final location, so nothing is left behind under the old one.
    stale: list[str] = [path for path in maps if "/impl/" in path]
    assert not stale, f"maps were written beside paths the pack no longer holds: {stale}"

    print(f"plugin_32: {len(EXPECTED)} functions mapped across a refactor that ran before mecha")

