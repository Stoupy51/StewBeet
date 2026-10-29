# Assertions for: stewbeet.plugins.source_maps on content built in variables

# Imports
import json
import os
from collections.abc import Iterator

from beet import Context, TextFile
from stouputils.typing import JsonDict

# Constants
EXPECTED: dict[str, dict[str, str]] = {
	"tns:grown": {
		"say grown head": "say grown head",
		"say grown loop alpha": "say grown loop {name}",
		"say grown loop again alpha": "say grown loop again {name}",
		"say grown loop gamma": "say grown loop {name}",
		"say grown loop again gamma": "say grown loop again {name}",
		"say grown tail": "say grown tail",
	},
	"tns:ended": {
		"say ended 0": 'ended += f"say ended {index}\\n"',
		"say ended 2": 'ended += f"say ended {index}\\n"',
	},
	"tns:started": {
		"say started 0": 'started += f"\\nsay started {index}"',
		"say started 2": 'started += f"\\nsay started {index}"',
	},
	"tns:reused_first": {
		"say reused first": "say reused first",
	},
	"tns:reused_second": {
		"say reused second": "say reused second",
		"say from helper": 'write_function("tns:reused_second", reused)',
		"say helper again": 'write_function("tns:reused_second", reused)',
		"say reused second tail": "say reused second tail",
	},
	"tns:branched": {
		"say branch taken": 'branched = "say branch taken\\n"',
		"say branch grown": 'branched += "say branch grown\\n"',
	},
	"tns:expanded": {
		"say expanded before": "say expanded before",
		"say inner one": "{block}",
		"say inner two": "{block}",
		"say expanded after": "say expanded after",
	},
}
""" Per function, a command it holds and the line of `link.py` that command must map to, stripped. """

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

	with open(os.path.join("src", "link.py"), encoding="utf-8") as file:
		source: list[str] = file.read().split("\n")

	for path, commands in EXPECTED.items():
		map_file = ctx.data.extra.get(f"data/{path.replace(':', '/function/', 1)}.mcfunction.map")
		assert isinstance(map_file, TextFile), f"{path} has no map"
		data: JsonDict = json.loads(map_file.text)
		assert [str(entry).replace("\\", "/") for entry in data["sources"]] == ["src/link.py"], \
			f"{path} maps to {data['sources']} rather than the file that wrote it"

		origins: dict[int, tuple[int, int, int]] = decode_mappings(str(data["mappings"]))
		generated: list[str] = ctx.data.functions[path].text.split("\n")
		for command, expected in commands.items():
			assert command in generated, f"{path} should hold {command!r}, got {generated}"
			index: int = generated.index(command)
			assert index in origins, f"{path}: {command!r} is not mapped"
			line: int = origins[index][1]
			assert source[line].strip() == expected, (
				f"{path}: {command!r} maps to link.py line {line + 1} ({source[line].strip()!r}) rather than {expected!r}"
			)

	print(f"plugin_39: {sum(len(commands) for commands in EXPECTED.values())} commands mapped to the literal line spelling them")

