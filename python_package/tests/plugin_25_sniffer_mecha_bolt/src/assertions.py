# Assertions for: stewbeet.plugins.sniffer.mecha

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


def source_of(data: JsonDict, generated_line: int) -> tuple[str, int, int]:
    """ Source file, 0-based line and 0-based column a generated line maps to. """
    index, line, column = decode_mappings(str(data["mappings"]))[generated_line]
    return str(list(data["sources"])[index]), line, column


def resolve(ctx: Context, data: JsonDict, path: str, source: str) -> list[str]:
    """ Lines of a mapped source, reached the way a consumer reaches it: sourceRoot then sources. """
    on_disk: str = os.path.join("build", str(ctx.data.name), path)
    resolved: str = os.path.normpath(os.path.join(os.path.dirname(on_disk), str(data["sourceRoot"]), source))
    assert os.path.isfile(resolved), f"{path}: sourceRoot + sources must resolve on disk, got {resolved}"
    with open(resolved, encoding="utf-8") as file:
        return file.read().split("\n")


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
    # Listed first and yielding, so these checks run after the emitter, mecha and auto.headers.
    yield

    maps: dict[str, JsonDict] = {
        path: json.loads(file.text)
        for path, file in ctx.data.extra.items()
        if path.endswith(".mcfunction.map") and isinstance(file, TextFile)
    }
    assert maps, "the mecha emitter must emit at least one .mcfunction.map"

    # Format conformance, the same contract plugin_22 holds the StewBeet producer to.
    for path, data in maps.items():
        assert data["version"] == 3, f"{path}: version must be 3, got {data['version']}"
        assert data["names"] == [], f"{path}: names must be empty for mcfunction"
        assert "sourcesContent" not in data, f"{path}: sourcesContent is not part of the format"
        assert data["sources"], f"{path}: a map with no sources should not have been written"
        for source in data["sources"]:
            assert "site-packages" not in str(source), f"{path}: source '{source}' leaks a library path"
            assert not os.path.isabs(str(source)), f"{path}: source '{source}' must be relative to sourceRoot"
        decoded = decode_mappings(str(data["mappings"]))
        assert list(decoded) == sorted(decoded), f"{path}: generated lines must be strictly increasing"

    # The minimal template's own example. `for i in range(1, 6)` writes one source line and mecha
    # emits five commands from it, so five generated lines share one origin. Getting this wrong by
    # walking the source down one line per command is the mistake the mapping exists to avoid.
    hello_path: str = "data/tns/function/hello.mcfunction.map"
    hello: JsonDict = maps[hello_path]
    hello_lines: list[str] = resolve(ctx, hello, hello_path, str(next(iter(hello["sources"]))))

    loop: list[tuple[str, int, int]] = [source_of(hello, 6 + offset) for offset in range(5)]
    assert len({(line, column) for _, line, column in loop}) == 1, \
        f"the five loop iterations come from one source position, got {loop}"
    say_line: int = loop[0][1]
    assert hello_lines[say_line].strip().startswith("say f"), \
        f"the loop's origin must be the say inside it, got {hello_lines[say_line]!r}"
    assert loop[0][2] == hello_lines[say_line].index("say"), "and its real column, not zero"

    # auto.headers prepends its block after mecha has compiled, so nothing lines up positionally.
    # Six unmapped lines before the first command is what the alignment pass is for.
    assert 0 not in decode_mappings(str(hello["mappings"])), "the header block has no origin and stays unmapped"

    # `execute function ./goodbye:` nests two more functions out of the same file, and the position
    # mecha kept is the `function` token inside that line rather than the start of it.
    goodbye_path: str = "data/tns/function/goodbye.mcfunction.map"
    goodbye: JsonDict = maps[goodbye_path]
    nested_file, nested_line, nested_column = source_of(goodbye, 7)
    assert nested_file.endswith("hello.mcfunction"), f"the nested call came from hello, got {nested_file}"
    assert hello_lines[nested_line].strip().startswith("execute function"), \
        f"the nested call maps to the execute that nested it, got {hello_lines[nested_line]!r}"
    assert hello_lines[nested_line][nested_column:].startswith("function"), \
        "column precision is the one thing this producer gets for free, and it is not being thrown away"

    # One function, two modules. This is the case a compilation unit's own filename gets wrong, and
    # it is the normal shape of a bolt project rather than an edge case.
    shared_path: str = "data/tns/function/shared.mcfunction.map"
    shared: JsonDict = maps[shared_path]
    assert len(shared["sources"]) == 2, f"shared was written by two modules, got {shared['sources']}"

    first_file, first_line, first_column = source_of(shared, 6)
    assert first_file.endswith("helper.bolt"), f"the first line came from helper.bolt, got {first_file}"
    assert (first_line, first_column) == (2, 4), \
        f"helper.bolt writes on line 3 column 5, got {first_line + 1}:{first_column + 1}"

    for generated_line, expected_line in ((7, 3), (8, 4)):
        file, line, column = source_of(shared, generated_line)
        assert file.endswith("main.bolt"), f"line {generated_line} came from main.bolt, got {file}"
        assert line == expected_line, f"line {generated_line} maps to line {expected_line + 1}, got {line + 1}"
        assert column == 4, f"line {generated_line} keeps its column, got {column + 1}"

    helper_lines: list[str] = resolve(ctx, shared, shared_path, first_file)
    assert helper_lines[first_line].strip() == "say from helper", \
        f"the mapped line must hold the command it produced, got {helper_lines[first_line]!r}"

    # A module outside the configured roots is emitted unmapped rather than named as a source.
    for path, data in maps.items():
        for source in data["sources"]:
            assert "vendor" not in str(source).replace(os.sep, "/").split("/"), \
                f"{path}: '{source}' is outside the project roots and may not be a mapping target"
    assert "data/tns/function/from_vendor.mcfunction.map" not in maps, \
        "a function written entirely by a vendored module has nothing to map"

    # Every mapped function carries the discovery comment, as its last line.
    for func_path, func in ctx.data.functions.items():
        if f"data/{func_path.replace(':', '/function/')}.mcfunction.map" not in maps:
            continue
        text: list[str] = func.text.rstrip("\n").split("\n")
        assert text[-1].startswith("## sourceMappingURL="), \
            f"{func_path}: last line must be the two-hash sourceMappingURL comment, got {text[-1]!r}"

    print(f"plugin_25: {len(maps)} maps verified across the minimal template's example and two bolt modules")

