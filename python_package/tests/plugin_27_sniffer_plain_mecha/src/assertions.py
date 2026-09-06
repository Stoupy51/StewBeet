# Assertions for: stewbeet.plugins.sniffer.mecha on a project with no bolt

# Imports
import json
import os
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
BASE64: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
""" The Source Map v3 alphabet, decoded here independently of the encoder under test. """


# Helpers
def decode_vlq(segment: str) -> list[int]:
    """ Decode one base64 VLQ segment into its signed fields. """
    values: list[int] = []
    accumulator: int = 0
    shift: int = 0
    for char in segment:
        digit: int = BASE64.index(char)
        accumulator += (digit & 31) << shift
        if digit & 32:
            shift += 5
        else:
            values.append(-(accumulator >> 1) if accumulator & 1 else accumulator >> 1)
            accumulator, shift = 0, 0
    return values


def decode_mappings(mappings: str) -> dict[int, tuple[int, int, int]]:
    """ Decode a mappings string into generated line -> (source index, source line, source column). """
    out: dict[int, tuple[int, int, int]] = {}
    source, line, column = 0, 0, 0
    for generated_line, group in enumerate(mappings.split(";")):
        if not group:
            continue
        fields: list[int] = decode_vlq(group)
        source += fields[1]
        line += fields[2]
        column += fields[3]
        out[generated_line] = (source, line, column)
    return out


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    # Listed first and yielding, so these checks run after the emitter and after mecha.
    yield

    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }

    # A real file mecha compiled maps to itself. This is the whole "mecha" dialect: no bolt, no
    # StewBeet helper, just a datapack compiled through mecha.
    on_disk_path: str = "data/tns/function/on_disk.mcfunction.map"
    assert on_disk_path in maps, f"a plain .mcfunction compiled by mecha must be mapped, got {sorted(maps)}"

    on_disk: JsonDict = maps[on_disk_path]
    assert len(on_disk["sources"]) == 1, on_disk["sources"]
    assert str(next(iter(on_disk["sources"]))).endswith("on_disk.mcfunction"), on_disk["sources"]

    origins: dict[int, tuple[int, int, int]] = decode_mappings(str(on_disk["mappings"]))
    assert origins, "the file has two commands and both should be mapped"
    for generated_line, (_, source_line, _) in origins.items():
        assert source_line == generated_line, (
            f"a file that compiles to itself maps line to line, got {generated_line} -> {source_line}"
        )

    # sourceRoot plus sources resolves, or navigation lands nowhere.
    resolved: str = os.path.normpath(os.path.join(
        "build", str(ctx.data.name), os.path.dirname(on_disk_path),
        str(on_disk["sourceRoot"]), str(next(iter(on_disk["sources"])))))
    assert os.path.isfile(resolved), f"sourceRoot + sources must resolve on disk, got {resolved}"

    # A Function assembled in Python has no file behind it. Its AST positions index into the
    # string it was parsed from, and the first character of that string is a valid position in
    # every file in the project, so a careless emitter maps it onto whichever one it finds.
    for path in ("assembled", "via_namespace"):
        assert f"data/tns/function/{path}.mcfunction.map" not in maps, (
            f"{path} was assembled in memory and has no source file, so it must be emitted unmapped"
        )
        assert "sourceMappingURL" not in ctx.data.functions[f"tns:{path}"].text, (
            f"{path} has no map, so it must not carry a discovery comment"
        )

    # And nothing anywhere may name a file that did not write it.
    for path, data in maps.items():
        for source in data["sources"]:
            assert str(source).endswith("on_disk.mcfunction"), (
                f"{path} names {source}, which is not where its commands came from"
            )

    print(f"plugin_27: {len(maps)} map(s) from plain mecha, assembled functions correctly unmapped")

