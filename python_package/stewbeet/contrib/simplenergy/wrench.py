
# Imports
from beet import FunctionTag

from ...core import Mem, set_json_encoder, write_function


# Setup simplenergy wrench rotatable tags and mechanization calls
def setup_wrench(blocks: list[str]) -> None:
	""" Setup rotatable tags for blocks and mechanization wrench calls.

	Args:
		blocks (list[str]): List of block names that should be rotatable. (e.g. ["furnace_generator", "electric_furnace", "electric_smelter", "pulverizer"])
	"""
	ns: str = Mem.ctx.project_id

	# Add tags for rotatables
	for rotatable in blocks:
		write_function(
			f"{ns}:custom_blocks/{rotatable}/place_secondary",
			f"\n# Make the block rotatable by wrench\ntag @s add {ns}.rotatable"
		)


	## Link with mechanization wrench
	# Link function tags
	json_content: dict[str, bool | list[str]] = {"required": False, "values": [f"{ns}:calls/mechanization/wrench_break"]}
	Mem.ctx.data["mechanization"].function_tags["wrench_break"] = set_json_encoder(FunctionTag(json_content))
	json_content = {"required": False, "values": [f"{ns}:calls/mechanization/wrench_modify"]}
	Mem.ctx.data["mechanization"].function_tags["wrench_modify"] = set_json_encoder(FunctionTag(json_content))

	# Write slots functions
	write_function(f"{ns}:calls/mechanization/wrench_break", f"""
execute if entity @s[tag={ns}.custom_block] run setblock ~ ~ ~ air destroy
execute if entity @s[tag={ns}.custom_block] run function {ns}:custom_blocks/destroy
""")
	write_function(
		f"{ns}:calls/mechanization/wrench_modify",
		f"execute if entity @s[tag={ns}.rotatable] run function {ns}:utils/wrench/rotate"
	)

