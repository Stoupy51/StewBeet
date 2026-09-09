# Assertions for: the sniffer requiring nothing else of StewBeet

# Imports
import json
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

from stewbeet.core import Mem
from stewbeet.plugins.sniffer.model import SourceOrigin, WriteChunk

# Constants
EXPECTED: tuple[str, ...] = ("tns:direct", "tns:appended", "tns:grown")
""" Every function this project writes, all of them through beet's own API. """

STALE: str = "/gone/previous_build.py"
""" A file no build of this project ever had. It reaches the map only if the plugin starts a build on what the last one left behind. """


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    # What a previous build in the same process leaves behind, which is what `beet watch` does.
    # This plugin is required before the sniffer, so this runs before it resets its own state.
    # `tns:grown` is assigned empty and grown by appends, so nothing overwrites this and clears it.
    Mem.source_map_chunks["tns:grown"] = [WriteChunk(
        lines=("say grown one", "say grown two"),
        origin=SourceOrigin(file=STALE, line=0, column=0),
    )]

    yield

    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }

    for path in EXPECTED:
        map_path: str = f"data/{path.replace(':', '/function/', 1)}.mcfunction.map"
        assert map_path in maps, f"{path} has no map, so the plugin needs a `stewbeet` it should not"
        sources: list[str] = [str(entry).replace("\\", "/") for entry in maps[map_path]["sources"]]
        assert sources == ["src/link.py"], f"{path} maps to {sources} rather than the file that wrote it"
        assert Mem.attribution == [], f"the attribution stack outlived the build: {Mem.attribution}"

    print(f"plugin_30: {len(EXPECTED)} functions mapped with no stewbeet plugin in the build")
