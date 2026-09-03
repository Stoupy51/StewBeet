
# Assertions for: stewbeet.plugins.sniffer under stewbeet.plugins.auto.headers

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
    # Runs on the way out, so the sniffer plugin has already emitted.
    yield

    ns: str = ctx.project_id
    map_path: str = f"data/{ns}/function/root.mcfunction.map"
    assert map_path in ctx.data.extra, "a map must still be written once auto.headers has rewritten every function"

    map_file = ctx.data.extra[map_path]
    assert isinstance(map_file, TextFile), f"{map_path} should have been written as a text file"
    data: JsonDict = json.loads(map_file.text)
    decoded: dict[int, tuple[int, int, int]] = decode_mappings(data["mappings"])
    generated: list[str] = ctx.data.functions[f"{ns}:root"].text.split("\n")

    # auto.headers rewrites the whole function with overwrite=True. A naive implementation clears
    # the recorded chunks there and loses every mapping in the pack, so this is the real test.
    assert decoded, "auto.headers must not destroy the mappings it rewrote around"

    # The header block it prepended has no author, so those lines stay unmapped.
    header_lines: list[int] = [i for i, line in enumerate(generated) if line.startswith("#>") or line.startswith("#")]
    assert header_lines, "the fixture must actually exercise auto.headers"
    for index in header_lines:
        if generated[index].startswith("## sourceMappingURL"):
            continue
        assert index not in decoded, \
            f"generated header line {index} ({generated[index]!r}) must be unmapped, it has no author"

    # Every real command still reaches the write_function call that wrote it.
    resolved_root: str = os.path.normpath(os.path.join(
        os.path.dirname(os.path.join("build", str(ctx.data.name), map_path)), data["sourceRoot"]))
    for index, (source_index, source_line, _) in decoded.items():
        source_file: str = os.path.join(resolved_root, data["sources"][source_index])
        assert os.path.isfile(source_file), f"source {source_file} must resolve from sourceRoot"
        with open(source_file, encoding="utf-8") as file:
            lines: list[str] = file.read().split("\n")
        assert source_line < len(lines), f"generated line {index} maps past the end of {source_file}"

    # G2 holds after the rewrite too.
    assert list(decoded) == sorted(decoded), "mapped generated lines must remain strictly increasing"

    # A command line the author wrote must still be mapped, not just the blanks around it.
    say_lines: list[int] = [i for i, line in enumerate(generated) if line.startswith("say Starting root")]
    assert say_lines, "fixture regression: 'say Starting root' should be in the output"
    assert say_lines[0] in decoded, \
        f"'say Starting root' (line {say_lines[0]}) lost its mapping when auto.headers rewrote the function"
