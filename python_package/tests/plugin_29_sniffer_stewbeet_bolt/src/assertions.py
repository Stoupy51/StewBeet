# Assertions for: one sniffer mapping a whole StewBeet project, bolt included

# Imports
import json
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
EXPECTED: dict[str, str] = {
    # Compiled by mecha out of a .mcfunction holding bolt, mapped off the AST.
    "tns:hello": "src/data/tns/function/hello.mcfunction",
    "tns:goodbye": "src/data/tns/function/hello.mcfunction",
    # Written by a StewBeet helper, mapped from what the capture recorded.
    "tns:written": "src/link.py",
}
""" Resource location to the source file its map must name. """


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    yield

    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }

    for path, source in EXPECTED.items():
        assert path in ctx.data.functions, f"{path} was not written into the pack at all"

        map_path: str = f"data/{path.replace(':', '/function/', 1)}.mcfunction.map"
        assert map_path in maps, f"{path} has no map, so navigation from it leads nowhere"
        sources: list[str] = [str(entry).replace("\\", "/") for entry in maps[map_path]["sources"]]
        assert sources == [source], f"{path} maps to {sources} rather than {source}"

    print(f"plugin_29: {len(EXPECTED)} functions mapped from one plugin in require")
