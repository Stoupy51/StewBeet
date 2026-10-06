# Assertions for: stewbeet.plugins.sniffer on a project with no bolt

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
	""" Decode a mappings string into generated line -> (source index, source line, source column) of its first segment. """
	out: dict[int, tuple[int, int, int]] = {}
	source, line, column = 0, 0, 0
	for generated_line, group in enumerate(mappings.split(";")):
		for index, segment in enumerate(filter(None, group.split(","))):
			fields: list[int] = decode_vlq(segment)
			source += fields[1]
			line += fields[2]
			column += fields[3]
			if index == 0:
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
	with open("src/data/tns/function/on_disk.mcfunction", encoding="utf-8") as file:
		source_lines: list[str] = file.read().splitlines()
	generated_lines: list[str] = ctx.data.functions["tns:on_disk"].text.splitlines()
	for generated_line, (_, source_line, _) in origins.items():
		assert source_lines[source_line] == generated_lines[generated_line], (
			f"a file that compiles to itself maps each command to its own line, got {generated_line} -> {source_line}"
		)

	# sourceRoot plus sources resolves, or navigation lands nowhere.
	resolved: str = os.path.normpath(os.path.join(
		"build", str(ctx.data.name), os.path.dirname(on_disk_path),
		str(on_disk["sourceRoot"]), str(next(iter(on_disk["sources"])))))
	assert os.path.isfile(resolved), f"sourceRoot + sources must resolve on disk, got {resolved}"

	# A Function assembled in Python maps to the line that assembled it. Its AST positions index into that string,
	# and any of them is a valid position in some project file, which a careless emitter would map it onto instead.
	with open("src/link.py", encoding="utf-8") as file:
		link_lines: list[str] = file.read().splitlines()
	for path, needle in (("assembled", '"tns:assembled"'), ("via_namespace", '["via_namespace"]')):
		assembled: JsonDict | None = maps.get(f"data/tns/function/{path}.mcfunction.map")
		assert assembled is not None, f"{path} was assembled in link.py and must map there, got {sorted(maps)}"
		assert [str(source) for source in assembled["sources"]] == ["src/link.py"], assembled["sources"]
		written_at: int = next(i for i, line in enumerate(link_lines) if needle in line)
		mapped_lines: set[int] = {line for _, line, _ in decode_mappings(str(assembled["mappings"])).values()}
		assert mapped_lines == {written_at}, f"{path} must map to link.py:{written_at}, got {mapped_lines}"

	# And nothing anywhere may name a file that did not write it.
	for path, data in maps.items():
		for source in data["sources"]:
			assert str(source).endswith(("on_disk.mcfunction", "link.py")), (
				f"{path} names {source}, which is not where its commands came from"
			)

	print(f"plugin_27: {len(maps)} map(s) from plain mecha, assembled functions mapped to the Python that assembled them")

