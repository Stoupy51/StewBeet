# Assertions for: what stewbeet.plugins.sniffer captures, and what it does not

# Imports
import json
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
EXPECTED: dict[str, int] = {
    # Through a StewBeet helper, which tags the Function with its path.
    "tns:written": 11,
    "tns:written_then_appended": 25,
    # beet's own idiom, caught by the hook on NamespaceContainer.process. Each maps to the line
    # that assigned it, whichever of the three spellings was used.
    "tns:direct_assign": 14,
    "tns:via_namespace": 15,
    "tns:via_filetype": 16,
    "tns:from_list": 17,
    # Assigned empty on line 22 and appended to on line 23. The append is what carries content,
    # so that is the line the first mapped command points at.
    "tns:appended": 22,
}
""" Resource location to the 0-based line of `link.py` its first mapped command comes from. """

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
    yield

    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }
    mapped: set[str] = {path.removeprefix("data/").removesuffix(".mcfunction.map").replace("/function/", ":", 1) for path in maps}

    # Every way of writing a function is mapped, and each to the line that wrote it.
    for path, expected_line in EXPECTED.items():
        assert path in ctx.data.functions, f"{path} was not written into the pack at all"
        assert path in mapped, f"{path} is not mapped, so navigation from it leads nowhere"

        map_path: str = f"data/{path.replace(':', '/function/', 1)}.mcfunction.map"
        origins = decode_mappings(str(maps[map_path]["mappings"]))
        assert origins, f"{path} has a map with no mapped line in it"

        source_index, source_line, _ = origins[min(origins)]
        source: str = str(list(maps[map_path]["sources"])[source_index])
        assert source.endswith("link.py"), f"{path} maps to {source} rather than the file that wrote it"
        assert source_line == expected_line, (
            f"{path} should map to link.py line {expected_line + 1}, got {source_line + 1}"
        )

    # Two helper writes to one path are two chunks of one map, not two maps, and each keeps its
    # own call site rather than both collapsing onto the first.
    both: JsonDict = maps["data/tns/function/written_then_appended.mcfunction.map"]
    origins: dict[int, tuple[int, int, int]] = decode_mappings(str(both["mappings"]))
    assert origins, "both writes went to one path, so that path has a map"

    # Both calls contributed, so the mapped lines span more than one place in link.py. The exact
    # count is not asserted: a literal's trailing newline maps its empty last line one line down,
    # which is step B's line-advance behaviour and not what this test is about.
    call_lines: set[int] = {line for _, line, _ in origins.values()}
    assert len(call_lines) > 1, f"both write calls should contribute, got one line {sorted(call_lines)}"
    assert all(str(list(both["sources"])[index]).endswith("link.py") for index, _, _ in origins.values()),         f"both chunks came from link.py, got {both['sources']}"

    # Every function carries a discovery comment now that every one of them has a map.
    for path in EXPECTED:
        assert "sourceMappingURL" in ctx.data.functions[path].text, (
            f"{path} has a map, so it must point at it"
        )

    print(f"plugin_26: {len(EXPECTED)} functions mapped across every way of writing one")

