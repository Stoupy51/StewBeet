
# Assertions for: stewbeet.plugins.sniffer

# Imports
import json
import os
import zipfile
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
BASE64: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
""" The Source Map v3 alphabet, decoded here independently of the encoder under test. """

LIBRARY_MARKERS: tuple[str, ...] = ("site-packages", "/stewbeet/", "/beet/", "/bolt/", "/mecha/", "/stouputils/")
""" Substrings that must never appear in a map's sources (G5). """


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
    # Runs on the way out, so the sniffer plugin has already emitted.
    yield

    ns: str = ctx.project_id
    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }

    # ── at least one map, and one per mapped function ─────────────────────────
    assert maps, "the sniffer plugin must emit at least one .mcfunction.map"

    for path, data in maps.items():
        # ── format conformance ────────────────────────────────────────────────
        assert data["version"] == 3, f"{path}: version must be 3, got {data['version']}"
        assert data["names"] == [], f"{path}: names must be empty for mcfunction"
        assert "sourcesContent" not in data, f"{path}: sourcesContent is not part of the format"
        assert data["sources"], f"{path}: a map with no sources should not have been written"
        assert data["file"].endswith(".mcfunction"), f"{path}: file must name the generated function"

        # sourceRoot climbs from the map's real on-disk directory to the project root
        on_disk: str = os.path.join("build", str(ctx.data.name), path)
        expected: int = len(os.path.dirname(on_disk).replace(os.sep, "/").split("/"))
        assert data["sourceRoot"] == "/".join([".."] * expected), \
            f"{path}: sourceRoot must climb from {os.path.dirname(on_disk)} to the project root"

        # ── G5: never a library file ─────────────────────────────────────────
        sources: list[str] = data["sources"]
        for source in sources:
            normalized: str = source.replace(os.sep, "/")
            for marker in LIBRARY_MARKERS:
                assert marker not in normalized, f"{path}: source '{source}' leaks library path '{marker}'"
            assert not os.path.isabs(source), f"{path}: source '{source}' must be relative to sourceRoot"

        # ── G2: mapped lines strictly increasing ─────────────────────────────
        mappings: str = data["mappings"]
        decoded = decode_mappings(mappings)
        assert list(decoded) == sorted(decoded), f"{path}: generated lines must be strictly increasing"

    # ── every function carries the discovery comment, as its LAST line ───────
    for func_path, func in ctx.data.functions.items():
        if f"data/{func_path.replace(':', '/function/')}.mcfunction.map" not in maps:
            continue
        lines: list[str] = func.text.rstrip("\n").split("\n")
        assert lines[-1].startswith("## sourceMappingURL="), \
            f"{func_path}: last line must be the two-hash sourceMappingURL comment, got {lines[-1]!r}"

    # ── the mapping actually lands on the write_function call in link.py ─────
    root_map: JsonDict = maps[f"data/{ns}/function/root.mcfunction.map"]
    root_mappings: str = root_map["mappings"]
    root_sources: list[str] = root_map["sources"]
    decoded = decode_mappings(root_mappings)
    assert decoded, "root must have at least one mapped line"

    link_source: str = root_sources[decoded[min(decoded)][0]]
    assert link_source.endswith("link.py"), f"root's first mapping must come from link.py, got {link_source}"

    root_on_disk: str = os.path.join("build", str(ctx.data.name), f"data/{ns}/function/root.mcfunction.map")
    resolved: str = os.path.normpath(os.path.join(
        os.path.dirname(root_on_disk), root_map["sourceRoot"], link_source))
    assert os.path.isfile(resolved), f"sourceRoot + sources must resolve on disk, got {resolved}"

    with open(resolved, encoding="utf-8") as file:
        source_lines: list[str] = file.read().split("\n")
    first_line: int = decoded[min(decoded)][1]
    assert "write_function" in source_lines[first_line], \
        f"root's first mapping must land on a write_function call, got {source_lines[first_line]!r}"

    # ── two call sites contributed to root, so its map carries both ─────────
    assert len(root_sources) >= 1, "root was written from more than one call site"
    lines_hit: set[int] = {line for _, line, _ in decoded.values()}
    assert len(lines_hit) > 1, f"root's mappings should span several source lines, got {sorted(lines_hit)}"

    # ── the zip the game loads carries the same thing the build directory does ──
    # This is the whole point of the emit step running before archive: a datapack is shipped to
    # saves/<world>/datapacks as this zip, so a map left out of it is a map the debugger never sees.
    archive: str = os.path.join("build", f"{ctx.project_name.replace(' ', '')}_datapack.zip")
    assert os.path.isfile(archive), f"the archive plugin should have produced {archive}"

    with zipfile.ZipFile(archive) as zip_file:
        entries: set[str] = set(zip_file.namelist())
        for path in maps:
            assert path in entries, f"{path} is missing from the archive, so Sniffer would never find it"

        for func_path in ctx.data.functions:
            entry: str = f"data/{func_path.replace(':', '/function/')}.mcfunction"
            if f"{entry}.map" not in maps:
                continue
            # beet serializes with the platform's line ending, so compare the text, not the bytes.
            zipped: str = zip_file.read(entry).decode("utf-8").replace("\r\n", "\n")
            assert zipped == ctx.data.functions[func_path].text, \
                f"{entry} differs between the archive and the build directory"
            assert zipped.rstrip("\n").split("\n")[-1].startswith("## sourceMappingURL="), \
                f"{entry} lost its discovery comment on the way into the archive"
