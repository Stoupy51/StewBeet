
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os

import stouputils as stp
from beet import LootTable
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import Block, GrowingSeed, GrowingSeedLoot
from ....core.cls.resource import Resource
from ....core.constants import GROWING_SEED, ITEMS_LOOT_FOLDER
from ....core.utils.io import set_json_encoder, write_function, write_load_file
from ....core.utils.loot_table import loot_function, loot_modifiers

# Constants
GROWTH_TICKS: tuple[tuple[int, str], ...] = ((60, "minute"), (5, "second_5"), (1, "second"))
""" Seconds added to the growth time per call, and the clock calling it, slowest first. """


# Functions
def write_growing_seed(obj_block: Block, growing_seed: GrowingSeed, item: str, source_textures: dict[str, str]) -> None:
	""" Write what makes a seed grow through its stages, and what it drops once fully grown. """
	ns: str = Mem.ctx.project_id
	write_function(obj_block.functions.place_secondary, f"""
# Update seed model
scoreboard players add @s {ns}.growth_time 0
function {obj_block.functions.update_seed_model}
""")
	texture_basename: str = growing_seed.texture_basename or item
	starts: str = f"{texture_basename}_stage_"
	num_stages: int = len({texture for texture in source_textures if os.path.basename(texture).startswith(starts)})
	write_update_seed_model(obj_block, num_stages, growing_seed.seconds)
	write_growth_tick(obj_block, item, num_stages - 1, growing_seed.seconds)

	loot_table: str | list[GrowingSeedLoot] = growing_seed.loots
	if not isinstance(loot_table, str):
		obj_block.seed_loot_table.write(set_json_encoder(LootTable(seed_loot_table(loot_table)), max_level=-1))
		loot_table = obj_block.seed_loot_table
	write_function(obj_block.functions.is_fully_grown, f"""
# If fully grown, drop the loot table and kill the current entity (item)
execute if score #growth_time {ns}.data matches {growing_seed.seconds}.. as @p[gamemode=!spectator] run loot spawn ~ ~ ~ fish {loot_table} ~ ~ ~ mainhand
execute if score #growth_time {ns}.data matches {growing_seed.seconds}.. run kill @s
""")  # noqa: E501


def write_update_seed_model(obj_block: Block, num_stages: int, growing_time: int) -> None:
	""" Switch the seed's model to the stage its growth time reached, the last stage being the grown plant. """
	ns: str = Mem.ctx.project_id
	progress_stages: int = num_stages - 1
	content: str = ""
	for stage in range(num_stages):
		time_from: int = int(stage * growing_time / progress_stages)
		time_to: int = int((stage + 1) * growing_time / progress_stages) - 1
		time_to_str: str = str(time_to) if stage < progress_stages else ""
		content += (
			f"execute if score @s {ns}.growth_time matches {time_from}..{time_to_str} "
			f"unless score @s {ns}.growth_stage matches {stage} run "
			f"""function {ns}:custom_blocks/change_seed_stage {{stage:{stage}, """
			f"""model:"{obj_block.seed_stage_item_model(stage)}"}}\n"""
		)
	write_function(obj_block.functions.update_seed_model, f"""
# Update growth stage based on growth_time
{content}
""")


def write_growth_tick(obj_block: Block, item: str, progress_stages: int, growing_time: int) -> None:
	""" Advance the growth time on the slowest clock that still reaches every stage on time. """
	ns: str = Mem.ctx.project_id
	speed, clock = next(((speed, clock) for speed, clock in GROWTH_TICKS if growing_time > speed * progress_stages), (0, ""))
	if not clock:
		stp.error(
			f"Growing seed '{item}' has a growing time < to the number of stages ({growing_time} seconds). "
			"Please increase the growing time or reduce the number of stages."
		)
		return
	write_function(obj_block.functions[clock], f"""
# Increment growth time score by {speed} and update model
scoreboard players add @s {ns}.growth_time {speed}
execute if score #boost_growth_time {ns}.data matches 1.. run scoreboard players operation @s {ns}.growth_time += #boost_growth_time {ns}.data
function {obj_block.functions.update_seed_model}
""")  # noqa: E501


def seed_loot_table(pools: list[GrowingSeedLoot]) -> JsonDict:
	""" The loot table a fully grown seed drops, one pool per loot.

	A pool's id is a vanilla item with `minecraft:`, one of this pack's items when plain, and another loot table otherwise.
	"""
	return {
		"type": "minecraft:block",
		"pools": [
			{
				"rolls": pool.rolls,
				"bonus_rolls": 0,
				"entries": [
					{
						"type": "minecraft:item" if "minecraft:" in pool.id else "minecraft:loot_table",
						"name" if "minecraft:" in pool.id else "value":
							(Resource(LootTable, f"{ITEMS_LOOT_FOLDER}/{pool.id}") if ":" not in pool.id else pool.id),
						**({} if not pool.fortune else loot_modifiers([
							loot_function(
								"minecraft:apply_bonus",
								enchantment="minecraft:fortune",
								formula="minecraft:binomial_with_bonus_count",
								parameters=pool.fortune,
							),
						]))
					}
				]
			}
			for pool in pools
		]
	}


def write_seed_functions(ns: str) -> None:
	""" The function switching a seed's stage and model, and the scores counting its growth. """
	write_function(f"{ns}:custom_blocks/change_seed_stage", f"""
# Update the growth stage score
$scoreboard players set @s {ns}.growth_stage $(stage)

# Change the item model to the right stage
$execute if entity @s[type=item_display] run return run data modify entity @s item.components."minecraft:item_model" set value "$(model)"
$execute if entity @s[type=item_frame] run return run data modify entity @s Item.components."minecraft:item_model" set value "$(model)"
""")  # noqa: E501
	write_load_file(f"""
# Create objectives for growing seeds
scoreboard objectives add {ns}.growth_time dummy
scoreboard objectives add {ns}.growth_stage dummy
""", prepend=True)


def write_seed_destroy(ns: str) -> None:
	""" Break a seed whose block below is no longer the one it is planted on. """
	content: str = ""
	for item, data in Mem.definitions.items():
		if data.get(GROWING_SEED):
			growing_seed: GrowingSeed = data[GROWING_SEED]
			content += (
				f"execute if score #total_{item} {ns}.data matches 1.. if entity @s[tag={ns}.{item}] "
				f"""unless block ~ ~-1 ~ {growing_seed.planted_on} """
				f"""run return run function {ns}:custom_blocks/no_block_below {{item:"{item}"}}\n"""
			)
	write_function(f"{ns}:custom_blocks/destroy_growing_seeds", content)
	write_function(f"{ns}:custom_blocks/no_block_below", f"""
# Break the block we're at and call the destroy function
execute if entity @s[type=item_frame] run summon item ~ ~ ~ {{Item:{{id:"minecraft:item_frame",count:1,components:{{"minecraft:custom_data":{{"{ns}":{{"item_frame_destroy":true}}}}}}}}}}
execute if entity @s[type=item_display] run setblock ~ ~ ~ air destroy
$function {ns}:custom_blocks/$(item)/destroy
""")  # noqa: E501

