# Assertions for: stewbeet.plugins.sniffer on a function edited before mecha compiled it

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


def decode_origins(mappings: str) -> dict[int, tuple[int, int]]:
	""" Generated line to (source index, source line), reading the first segment of each line. """
	out: dict[int, tuple[int, int]] = {}
	source: int = 0
	line: int = 0
	for generated_line, group in enumerate(mappings.split(";")):
		if not group:
			continue
		fields: list[int] = decode_vlq(group.split(",")[0])
		source += fields[1]
		line += fields[2]
		out[generated_line] = (source, line)
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
	sources: list[str] = [str(source) for source in source_map["sources"]]
	origins: dict[int, tuple[int, int]] = decode_origins(str(source_map["mappings"]))

	# The prepended line comes from the Python that prepended it
	with open("src/prepend.py", encoding="utf-8") as file:
		prepend_line: int = next(i for i, line in enumerate(file.read().splitlines()) if ".prepend(" in line)
	assert generated[0] == "scoreboard objectives add tns.math dummy", generated
	assert 0 in origins and sources[origins[0][0]].endswith("prepend.py") and origins[0][1] == prepend_line, (
		f"the prepended line must map to prepend.py:{prepend_line}, got {origins.get(0)} over {sources}"
	)

	# And every command written on disk to its own line there
	from_disk: dict[int, int] = {
		generated_line: line for generated_line, (source, line) in origins.items() if sources[source].endswith("load.mcfunction")
	}
	for generated_line, source_line in from_disk.items():
		assert on_disk[source_line] == generated[generated_line], (
			f"generated line {generated_line} '{generated[generated_line]}' maps to '{on_disk[source_line]}' on disk"
		)
	assert len(from_disk) == 3, f"each of the three commands written on disk is mapped, got {origins}"

	print("plugin_35: an edited function maps to the lines on disk, and the added line to the Python that added it")

