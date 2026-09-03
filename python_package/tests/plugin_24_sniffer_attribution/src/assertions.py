# Assertions for: attribution scopes (step B2)

# Imports
import json
import os
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
BASE64: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
""" The Source Map v3 alphabet, decoded here independently of the encoder under test. """

LIBRARY_MARKERS: tuple[str, ...] = ("site-packages", "/stewbeet/", "/beet/", "/bolt/", "/mecha/", "/stouputils/")
""" Substrings that must never appear in a map's sources. """

BLOCK_ID: str = "attributed_block"
""" The one declaration this fixture makes. """


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


def line_holding(path: str, needle: str) -> int:
    """ 0-based line of the first line of code holding `needle`, so no line number is hardcoded.

    Comments are skipped, since these fixtures describe in prose the very call they look for.
    """
    with open(os.path.join("src", path), encoding="utf-8") as file:
        lines: list[str] = file.read().split("\n")
    for index, line in enumerate(lines):
        if needle in line and not line.lstrip().startswith("#"):
            return index
    raise AssertionError(f"src/{path} no longer holds '{needle}', the fixture is broken")


def sources_of(source_map: JsonDict) -> list[str]:
    """ The `sources` array, typed, since everything below indexes it. """
    sources: list[str] = source_map["sources"]
    return sources


def mappings_of(source_map: JsonDict) -> dict[int, tuple[int, int, int]]:
    """ The decoded line table of one map. """
    mappings: str = source_map["mappings"]
    return decode_mappings(mappings)


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    # Runs on the way out, so custom_blocks, link and the emit step have all finished.
    yield

    ns: str = ctx.project_id
    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }
    assert maps, "the sniffer plugin must emit at least one .mcfunction.map"

    # ── US1: generated block content maps to the declaration, never to a library ──
    declared: int = line_holding("definitions.py", "Block(")
    generated_maps: dict[str, JsonDict] = {
        path: data for path, data in maps.items()
        if f"custom_blocks/{BLOCK_ID}/" in path
    }
    assert generated_maps, f"custom_blocks should have generated mapped functions for {BLOCK_ID}, got {sorted(maps)}"

    hit_declaration: bool = False
    for path, data in generated_maps.items():
        for source_index, source_line, _ in mappings_of(data).values():
            source: str = sources_of(data)[source_index]
            assert source.endswith(("definitions.py", "link.py")), \
                f"{path}: generated content should map to the fixture's own files, got {source}"
            if source.endswith("definitions.py"):
                assert source_line == declared, \
                    f"{path}: a declaration-attributed line should point at the Block( call on line {declared}, got {source_line}"
                hit_declaration = True
    assert hit_declaration, "no generated line was attributed to the declaration, tier 2 never fired"

    # ── the two negatives, which is what catches a broken tier order ─────────────
    for path, data in maps.items():
        for source in sources_of(data):
            normalized: str = source.replace(os.sep, "/")
            for marker in LIBRARY_MARKERS:
                assert marker not in normalized, f"{path}: source '{source}' leaks library path '{marker}'"
            assert not normalized.endswith("assertions.py"), \
                f"{path}: mapped to this pipeline's own entry point, which authored nothing"

    # ── pack-level scaffolding belongs to no declaration and stays unmapped ──────
    for path in maps:
        assert "custom_blocks/get_rotation" not in path, \
            "get_rotation is written before the loop and belongs to no declaration, it must stay unmapped"

    # ── US2: the author's own append keeps its own line, after the generated ones ─
    secondary: str = f"data/{ns}/function/custom_blocks/{BLOCK_ID}/place_secondary.mcfunction.map"
    assert secondary in maps, f"expected a map for place_secondary, got {sorted(maps)}"

    decoded: dict[int, tuple[int, int, int]] = mappings_of(maps[secondary])
    sources: list[str] = sources_of(maps[secondary])
    assert len(sources) == 2, f"place_secondary should carry both origins, got {sources}"

    appended_at: int = line_holding("link.py", ".obj.append(")
    appended: list[int] = [
        generated for generated, (index, line, _) in decoded.items()
        if sources[index].endswith("link.py") and line == appended_at
    ]
    assert appended, f"the .obj.append line should map to link.py:{appended_at}, got {decoded} over {sources}"

    from_declaration: list[int] = [
        generated for generated, (index, _, _) in decoded.items()
        if sources[index].endswith("definitions.py")
    ]
    assert from_declaration, "place_secondary lost its declaration-attributed lines"
    assert min(appended) > max(from_declaration), \
        f"the append happened after the generation, so its lines come after: {appended} vs {from_declaration}"

