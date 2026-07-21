
# pyright: reportArgumentType=false
# Imports
from beet import FunctionTag

from ...core import CUSTOM_BLOCKS_FOLDER, Block, BlockFunctions, Mem, set_json_encoder, write_function


# Setup simplenergy wrench rotatable tags and mechanization calls
def setup_wrench(blocks: list[str] | str, tag_ns: str = "simplenergy") -> None:
	""" Setup rotatable tags for blocks and mechanization wrench calls.

	Args:
		blocks (list[str]): List of block names that should be rotatable. (e.g. ["furnace_generator", "electric_furnace", "electric_smelter", "pulverizer"])
		tag_ns (str): Namespace for the tags. Default is "simplenergy".
	"""
	ns: str = Mem.ctx.project_id
	if isinstance(blocks, str):
		blocks = [x for x, y in Mem.definitions.items() if y.get("vanilla_block") and Block.from_id(x).vanilla_block.get("block_facing") == "player"]

	# Add tags for rotatables
	for rotatable in blocks:
		write_function(
			BlockFunctions(rotatable).place_secondary,
			f"\n# Make the block rotatable by wrench\ntag @s add {tag_ns}.rotatable"
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
execute if entity @s[tag={ns}.custom_block] run function {ns}:{CUSTOM_BLOCKS_FOLDER}/destroy
""")
	write_function(
		f"{ns}:calls/mechanization/wrench_modify",
		f"execute if entity @s[tag={tag_ns}.rotatable] run function {tag_ns}:utils/wrench/rotate"
	)

