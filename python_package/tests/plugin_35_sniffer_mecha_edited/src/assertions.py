# Assertions for: stewbeet.plugins.sniffer.mecha on a function edited before mecha compiled it

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


def decode_lines(mappings: str) -> dict[int, int]:
	""" Generated line to source line, reading the first segment of each line. """
	out: dict[int, int] = {}
	line: int = 0
	for generated_line, group in enumerate(mappings.split(";")):
		if not group:
			continue
		line += decode_vlq(group.split(",")[0])[2]
		out[generated_line] = line
	return out


# Main entry point
def beet_default(ctx: Context) -> Iterator[None]:
	# Listed first and yielding, so these checks run after the emitter and after mecha.
	yield

	extra = ctx.data.extra.get("data/tns/function/load.mcfunction.map")
	assert isinstance(extra, TextFile), "the edited load function must still be mapped"
	source_map: JsonDict = json.loads(extra.text)

	with open("src/data/tns/function/load.mcfunction", encoding="utf-8") as file:
		on_disk: list[str] = file.read().splitlines()
	generated: list[str] = ctx.data.functions["tns:load"].text.splitlines()
	origins: dict[int, int] = decode_lines(str(source_map["mappings"]))

	assert generated[0] == "scoreboard objectives add tns.math dummy", generated
	assert 0 not in origins, "the prepended line is in no file, so it maps nowhere"
	for generated_line, source_line in origins.items():
		assert on_disk[source_line] == generated[generated_line], (
			f"generated line {generated_line} '{generated[generated_line]}' maps to '{on_disk[source_line]}' on disk"
		)
	assert len(origins) == 3, f"each of the three commands written on disk is mapped, got {origins}"

	print("plugin_35: an edited function maps to the lines on disk, and the added line to nothing")

