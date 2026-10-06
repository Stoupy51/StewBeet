""" 🧱 Sets up the custom blocks of the definitions in the datapack. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from pathlib import Path

import stouputils as stp
from beet import Context, EntityTypeTag, Predicate
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import Block
from ....core.constants import CUSTOM_BLOCK_ALTERNATIVE, VANILLA_BLOCK
from ....core.utils.io import set_json_encoder, write_function
from ....core.utils.loot_table import loot_condition
from ... import sniffer
from .destroying import (
	write_block_destroys,
	write_destroy_dispatch,
	write_groups,
	write_periodic_checks,
	write_signal_listeners,
	write_vanilla_checks,
)
from .placing import FACING, write_head_searches, write_placement, write_smithed_link
from .seeds import write_growing_seed, write_seed_destroy, write_seed_functions


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.datapack.custom_blocks'")
def beet_default(ctx: Context):
	""" Main entry point for the custom blocks plugin.
	This plugin sets up custom blocks in the datapack based of the given definitions configuration.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx
	ns: str = ctx.project_id
	textures_folder: str = stp.relative_path(ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	assert textures_folder != "", (
		"Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. "
		"Please set a directory path in project configuration."
	)
	source_textures: dict[str, str] = {
		stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
		for p in sorted(Path(textures_folder).rglob("*.png"), key=str)
	}
	warn_unplaceable_blocks()
	if not any(data.get(VANILLA_BLOCK) for data in Mem.definitions.values()):
		return

	write_shared_functions(ns)
	unique_blocks: set[str] = set()
	custom_block_entities: set[str] = set()
	has_growing_seed: bool = False
	for item, data in sniffer.attributed(Mem.definitions.items()):
		if not data.get(VANILLA_BLOCK):
			continue
		obj_block: Block = Block.from_id(item)

		placed: tuple[str, str] | None = write_placement(obj_block, item, data)
		if placed is not None:
			unique_blocks.add(placed[0])
			custom_block_entities.add(placed[1])
		if obj_block.growing_seed:
			has_growing_seed = True
			write_growing_seed(obj_block, obj_block.growing_seed, item, source_textures)
	if has_growing_seed:
		write_seed_functions(ns)
	write_smithed_link(ns)

	# Custom block alternative last
	unique_blocks_sorted: list[str] = sorted(unique_blocks, key=lambda x: (x == CUSTOM_BLOCK_ALTERNATIVE, x))
	write_destroy_dispatch(ns, unique_blocks_sorted)
	if has_growing_seed:
		write_seed_destroy(ns)
	write_groups(ns, unique_blocks_sorted)
	write_block_destroys(ns)
	write_vanilla_checks(ns, unique_blocks_sorted)
	write_periodic_checks(ns, has_growing_seed)
	ctx.data[ns].entity_type_tags["custom_blocks"] = set_json_encoder(EntityTypeTag({"values": sorted(custom_block_entities)}))
	write_signal_listeners(ns)
	write_stats_totals(ns, has_growing_seed)
	write_head_searches(ns)


# Functions
def warn_unplaceable_blocks() -> None:
	""" Warn about the blocks without a vanilla block, which nothing can place. """
	incomplete_blocks: list[str] = [
		item for item, data in Mem.definitions.items() if isinstance(data, Block) and data.vanilla_block is None
	]
	if incomplete_blocks:
		stp.warning(
			f"Blocks without a vanilla_block won't be placeable: {incomplete_blocks}. "
			f"Set one in your definitions, e.g. "
			f"Block.from_id({incomplete_blocks[0]!r}).vanilla_block = VanillaBlock(id=\"minecraft:iron_block\")"
		)


def write_shared_functions(ns: str) -> None:
	""" The facing and light predicates, and the rotation and brightness functions every custom block uses. """
	for face in FACING:
		pred: JsonDict = loot_condition("minecraft:location_check", predicate={"block":{"state":{"facing":face}}})
		Mem.ctx.data[ns].predicates[f"facing/{face}"] = set_json_encoder(Predicate(pred))

	# Light level predicates (for dynamic brightness computation)
	for level in range(1, 16):
		light_pred: JsonDict = loot_condition("minecraft:location_check", predicate={"light": {"light": level}})
		Mem.ctx.data[ns].predicates[f"light/{level}"] = set_json_encoder(Predicate(light_pred), max_level=-1)

	# Get rotation function
	write_function(f"{ns}:custom_blocks/get_rotation",
f"""
# Set up score
scoreboard players set #rotation {ns}.data 0

# Player case
execute if score #rotation {ns}.data matches 0 if entity @s[y_rotation=-46..45] run scoreboard players set #rotation {ns}.data 1
execute if score #rotation {ns}.data matches 0 if entity @s[y_rotation=45..135] run scoreboard players set #rotation {ns}.data 2
execute if score #rotation {ns}.data matches 0 if entity @s[y_rotation=135..225] run scoreboard players set #rotation {ns}.data 3
execute if score #rotation {ns}.data matches 0 if entity @s[y_rotation=225..315] run scoreboard players set #rotation {ns}.data 4

# Predicate case
execute if score #rotation {ns}.data matches 0 if predicate {ns}:facing/north run scoreboard players set #rotation {ns}.data 1
execute if score #rotation {ns}.data matches 0 if predicate {ns}:facing/east run scoreboard players set #rotation {ns}.data 2
execute if score #rotation {ns}.data matches 0 if predicate {ns}:facing/south run scoreboard players set #rotation {ns}.data 3
execute if score #rotation {ns}.data matches 0 if predicate {ns}:facing/west run scoreboard players set #rotation {ns}.data 4
# No more cases for now
""")
	# Check light level at current position and update #light score if higher
	check_light_lines: str = "".join(
		f"execute if score #light {ns}.data matches ..{level - 1} if predicate {ns}:light/{level} "
		f"run return run scoreboard players set #light {ns}.data {level}\n"
		for level in range(1, 16)
	)
	write_function(f"{ns}:custom_blocks/check_light", f"""
# Check light level at current position and update #light if higher
{check_light_lines}""")

	# Compute the brightness of a custom block by sampling all 6 neighboring positions
	FACES: list[str] = ["~ ~1 ~", "~ ~-1 ~", "~1 ~ ~", "~-1 ~ ~", "~ ~ ~1", "~ ~ ~-1"]
	compute_brightness_lines: str = "".join(
		f"execute if score #light {ns}.data matches ..14 positioned {face} run function {ns}:custom_blocks/check_light\n"
		for face in FACES
	)
	write_function(f"{ns}:custom_blocks/compute_brightness", f"""
# Reset light score
scoreboard players set #light {ns}.data 0

# Check all 6 neighboring positions
{compute_brightness_lines}
# Apply computed brightness to the entity
data merge entity @s {{brightness:{{block:0,sky:0}}}}
execute store result entity @s brightness.block int 1 run scoreboard players get #light {ns}.data
execute store result entity @s brightness.sky int 1 run scoreboard players get #light {ns}.data
""")


def write_stats_totals(ns: str, has_growing_seed: bool) -> None:
	""" The stats lines counting every custom block, and every growing seed when there are any. """
	write_function(f"{ns}:_stats_custom_blocks",
		f'tellraw @s [{{"text":"- Total custom blocks: ","color":"dark_aqua"}},'
		f'{{"score":{{"name":"#total_custom_blocks","objective":"{ns}.data"}},"color":"aqua"}}]'
	)
	write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #total_custom_blocks {ns}.data 0', prepend = True)
	if has_growing_seed:
		write_function(f"{ns}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- Total growing seeds: ","color":"dark_aqua"}},'
			f'{{"score":{{"name":"#total_growing_seeds","objective":"{ns}.data"}},"color":"aqua"}}]'
		)
		write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #total_growing_seeds {ns}.data 0', prepend = True)

