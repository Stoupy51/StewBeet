# Assertions for: the bolt, columns and opaque data of stewbeet.plugins.sniffer.mecha

# Imports
import json
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


def decode_points(mappings: str) -> dict[int, list[tuple[int, int, int]]]:
	""" Generated line to every (generated column, source line, source column) segment on it. """
	out: dict[int, list[tuple[int, int, int]]] = {}
	line, column = 0, 0
	for generated_line, group in enumerate(mappings.split(";")):
		generated: int = 0
		for segment in filter(None, group.split(",")):
			fields: list[int] = decode_vlq(segment)
			generated += fields[0]
			line += fields[2]
			column += fields[3]
			out.setdefault(generated_line, []).append((generated, line, column))
	return out


def value_between(points: list[tuple[int, int, int]], text: str, line: int, start: str, source: list[str]) -> str:
	""" What the generated line holds between the points at both ends of `start` on a source line. """
	begin: int = source[line].index(start)
	ends: dict[int, int] = {column: generated for generated, point_line, column in points if point_line == line}
	return text[ends[begin]:ends[begin + len(start)]]


def map_of(ctx: Context, name: str) -> JsonDict:
	extra = ctx.data.extra.get(f"data/tns/function/{name}.mcfunction.map")
	assert isinstance(extra, TextFile), f"{name} must be mapped"
	return json.loads(extra.text)


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
	# Listed first and yielding, so these checks run after the emitter and after mecha.
	yield

	main: JsonDict = map_of(ctx, "main")
	assert main.get("x_stewbeet_bolt") == [0], f"main.mcfunction is bolt, got {main.get('x_stewbeet_bolt')}"
	assert "x_stewbeet_bolt" not in map_of(ctx, "plain"), "a file of plain commands is vanilla, bolt loaded or not"
	assert map_of(ctx, "spread").get("x_stewbeet_bolt") == [0], "a command over three lines is mecha's, not vanilla's"

	with open("src/data/tns/function/main.mcfunction", encoding="utf-8") as file:
		source: list[str] = file.read().splitlines()
	generated: list[str] = ctx.data.functions["tns:main"].text.splitlines()
	points: dict[int, list[tuple[int, int, int]]] = decode_points(str(main["mappings"]))
	by_source: dict[int, int] = {segments[0][1]: line for line, segments in points.items()}

	# A value bolt computed and a path mecha resolved, each given back between the same two points.
	storage: int = by_source[2]
	assert value_between(points[storage], generated[storage], 2, "int(major)", source) == "2", generated[storage]
	schedule: int = by_source[5]
	assert generated[schedule] == "schedule function tns:main 1 replace", generated[schedule]
	assert value_between(points[schedule], generated[schedule], 5, "~/", source) == "tns:main", (
		"`1t` became `1`, which is exactly what a text alignment cannot see past"
	)
	execute: int = by_source[3]
	assert value_between(points[execute], generated[execute], 3, "~/child", source) == "tns:main/child", generated[execute]

	# `say loudly` is in no vanilla tree, and it is the plugin's word `loudly` the build says the vanilla syntax ends at.
	assert main.get("x_stewbeet_opaque") == [[0, 6, 4]], f"got {main.get('x_stewbeet_opaque')}"
	assert "x_stewbeet_opaque" not in map_of(ctx, "plain")

	print("plugin_36: bolt sources, node columns and plugin syntax all reach the map")

