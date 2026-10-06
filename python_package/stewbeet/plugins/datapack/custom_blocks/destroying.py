
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet import BlockTag, LootTable, Predicate
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import VANILLA_BLOCK_FOR_ORES, Block, NoSilkTouchDrop
from ....core.cls.item import Item
from ....core.constants import CUSTOM_BLOCK_ALTERNATIVE, GROWING_SEED, NO_SILK_TOUCH_DROP, VANILLA_BLOCK
from ....core.utils.io import set_json_encoder, write_function, write_versioned_function
from ....core.utils.loot_table import loot_condition

# Constants
VANILLA_BLOCKS_TAG: str = "used_vanilla_blocks"
""" The block tag listing every vanilla block a custom block stands in. """


# Functions
def vanilla_block_of(vanilla_block: JsonDict) -> str | None:
	""" The vanilla block a custom block stands in, without its states or data, `CUSTOM_BLOCK_ALTERNATIVE` for an item frame block.

	>>> vanilla_block_of({"id": "minecraft:furnace[lit=false]"}), vanilla_block_of({"contents": True}), vanilla_block_of({})
	('minecraft:furnace', 'minecraft:item_frame', None)
	"""
	if vanilla_block.get("id"):
		return vanilla_block["id"].split('[')[0].split('{')[0]
	if vanilla_block.get("contents", False):
		return CUSTOM_BLOCK_ALTERNATIVE
	return None


def write_destroy_dispatch(ns: str, unique_blocks: list[str]) -> None:
	""" Send a custom block whose vanilla block went missing to the group of blocks sharing that vanilla block. """
	content: str = "# Check for missing vanilla blocks\n"
	for block_id in unique_blocks:
		score_check: str = f"score #total_vanilla_{block_id.replace('minecraft:','')} {ns}.data matches 1.."
		block_underscore: str = block_id.replace(":","_")
		if block_id == CUSTOM_BLOCK_ALTERNATIVE:
			content += (
				f"execute if {score_check} if entity @s[tag={ns}.vanilla.{block_underscore}] "
				f"unless items entity @s contents *[minecraft:custom_data~{{{ns}:{{item_frame_destroy:true}}}}] "
				f"run return run function {ns}:custom_blocks/_groups/{block_underscore}\n"
			)
			continue
		# The cauldron changes block id as it fills
		matched: str = "#minecraft:cauldrons" if block_id == "minecraft:cauldron" else block_id
		content += (
			f"execute if {score_check} if entity @s[tag={ns}.vanilla.{block_underscore}] "
			f"unless block ~ ~ ~ {matched} run return run function {ns}:custom_blocks/_groups/{block_underscore}\n"
		)
	write_function(f"{ns}:custom_blocks/destroy", content)


def write_groups(ns: str, unique_blocks: list[str]) -> None:
	""" Per vanilla block, its stats line and the group function destroying whichever custom block it was. """
	for block_id in unique_blocks:
		score_name: str = f"total_vanilla_{block_id.replace('minecraft:','')}"
		write_function(f"{ns}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- Vanilla \'{block_id}\': ","color":"gray"}},'
			f'{{"score":{{"name":"#{score_name}","objective":"{ns}.data"}},"color":"white"}}]'
		)
		write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #{score_name} {ns}.data 0', prepend = True)

		content: str = "\n" + "".join(
			f"execute if score #total_{item} {ns}.data matches 1.. if entity @s[tag={ns}.{item}] "
			f"run function {Block.from_id(item).functions.destroy}\n"
			for item, data in Mem.definitions.items()
			if data.get(VANILLA_BLOCK) and vanilla_block_of(data[VANILLA_BLOCK]) == block_id
		)
		write_function(f"{ns}:custom_blocks/_groups/{block_id.replace(':','_')}", content + "\n")


def write_block_destroys(ns: str) -> None:
	""" Per custom block, the destroy function and the one turning the vanilla drop into the custom item. """
	for item, data in Mem.definitions.items():
		if not data.get(VANILLA_BLOCK):
			continue
		block_id: str | None = vanilla_block_of(data[VANILLA_BLOCK])
		if block_id is not None:
			write_block_destroy(ns, item, data, block_id)


def write_block_destroy(ns: str, item: str, data: Item, block_id: str) -> None:
	""" Write the destroy function of one custom block standing in `block_id`, and its replace_item function. """
	obj_block: Block = Block.from_id(item)
	item_nbt: str = f"""{{id:"{block_id}"}}"""
	if block_id == CUSTOM_BLOCK_ALTERNATIVE:
		item_nbt = f"""{{components:{{"minecraft:custom_data":{{"{ns}":{{"item_frame_destroy":true}}}}}}}}"""
	growth_line: str = f"\nscoreboard players operation #growth_time {ns}.data = @s {ns}.growth_time" if data.get(GROWING_SEED) else ""
	write_function(obj_block.functions.destroy, f"""
# Replace the item with the custom one{growth_line}
execute as @n[type=item,nbt={{Item:{item_nbt}}},distance=..1] run function {obj_block.functions.replace_item}

# Decrease count scores
scoreboard players remove #total_custom_blocks {ns}.data 1
scoreboard players remove #total_vanilla_{block_id.replace('minecraft:','')} {ns}.data 1
scoreboard players remove #total_{item} {ns}.data 1

# Kill the custom block entity
kill @s
""")

	content: str = f"""
# Replace the item with the custom one
data modify entity @s Item.components set from storage {ns}:items all.{item}.components
data modify entity @s Item.id set from storage {ns}:items all.{item}.id
"""
	if data.get(NO_SILK_TOUCH_DROP):
		content = no_silk_touch_content(ns, item, data, obj_block, item_nbt)
	if data.get(GROWING_SEED):
		content += f"""
# Check if the seed is fully grown
function {obj_block.functions.is_fully_grown}
"""
	write_function(obj_block.functions.replace_item, content)


def no_silk_touch_content(ns: str, item: str, data: Item, obj_block: Block, item_nbt: str) -> str:
	""" The replace_item commands of a block dropping something else unless mined with silk touch.

	An ore relies on common_signals for the silk touch and the count, any other block checks the player's tool itself.
	"""
	is_ore: bool = data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES
	if not is_ore:
		write_function(obj_block.functions.destroy, f"""
# Check if the player has silk touch in mainhand
scoreboard players set #is_silk_touch {ns}.data 0
execute as @p[distance=..10,gamemode=!spectator] if data entity @s SelectedItem.components."minecraft:enchantments"."minecraft:silk_touch" run scoreboard players set #is_silk_touch {ns}.data 1

# If no item found, summon it
execute unless entity @n[type=item,nbt={{Item:{item_nbt}}},distance=..1] run loot spawn ~ ~ ~ loot {{pools:[{{entries:[{{type:"minecraft:item",name:"minecraft:glass"}}],rolls:1}}]}}
""", prepend=True)  # noqa: E501

	no_silk_touch_drop: str | JsonDict | NoSilkTouchDrop | LootTable = data[NO_SILK_TOUCH_DROP]
	if isinstance(no_silk_touch_drop, LootTable):
		no_silk_loot_table = obj_block.no_silk_touch_loot_table
		no_silk_loot_table.write(set_json_encoder(no_silk_touch_drop, max_level=-1))
		content: str = f"""
# If silk touch applied
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.id set from storage {ns}:items all.{item}.id
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.components set from storage {ns}:items all.{item}.components

# Else, no silk touch
execute if score #is_silk_touch {ns}.data matches 0 positioned ~ ~ ~ as @p[distance=..10,gamemode=!spectator] run loot spawn ~ ~ ~ fish {no_silk_loot_table} ~ ~ ~ mainhand
execute if score #is_silk_touch {ns}.data matches 0 unless entity @p[distance=..10,gamemode=!spectator] run loot spawn ~ ~ ~ loot {no_silk_loot_table}
execute if score #is_silk_touch {ns}.data matches 0 run kill @s
"""  # noqa: E501
		if is_ore:
			content += f"""
# Keep item count when silk touch is applied
execute if score #is_silk_touch {ns}.data matches 1 store result entity @s Item.count byte 1 run scoreboard players get #item_count {ns}.data
"""  # noqa: E501
		return content

	content = f"""
# If silk touch applied
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.id set from storage {ns}:items all.{item}.id
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.components set from storage {ns}:items all.{item}.components

# Else, no silk touch
{no_silk_touch_drop_lines(ns, no_silk_touch_drop)}
"""  # noqa: E501
	if is_ore:
		content += f"""
# Get item count in every case
execute store result entity @s Item.count byte 1 run scoreboard players get #item_count {ns}.data
"""
	return content


def no_silk_touch_drop_lines(ns: str, drop: str | JsonDict | NoSilkTouchDrop) -> str:
	""" The commands turning the vanilla drop into `drop`, an item id or a count of one, when no silk touch was used. """
	if isinstance(drop, str):
		item_to_drop, count_min, count_max = drop, 1, 1
	elif isinstance(drop.get("count"), int):
		item_to_drop, count_min, count_max = drop["id"], drop["count"], drop["count"]
	else:
		item_to_drop, count_min, count_max = drop["id"], drop["count"]["min"], drop["count"]["max"]

	when_no_silk: str = f"\nexecute if score #is_silk_touch {ns}.data matches 0"
	if ':' in item_to_drop:
		lines: str = f'execute if score #is_silk_touch {ns}.data matches 0 run data modify entity @s Item.id set value "{item_to_drop}"'  # noqa: E501
	else:
		lines = (
			f"execute if score #is_silk_touch {ns}.data matches 0 "
			f"run data modify entity @s Item.id set from storage {ns}:items all.{item_to_drop}.id"
			f"{when_no_silk} run data modify entity @s Item.components set from storage {ns}:items all.{item_to_drop}.components"
		)
	if count_min == count_max and count_min != 1:
		lines += f"{when_no_silk} run scoreboard players set #multiplier {ns}.data {count_min}"
		lines += f"{when_no_silk} run scoreboard players operation #item_count {ns}.data *= #multiplier {ns}.data"
	elif count_min < count_max:
		lines += f"{when_no_silk} run scoreboard players set #divider {ns}.data 100"
		lines += f"{when_no_silk} store result score #multiplier {ns}.data run random value {count_min*100}..{count_max*100}"
		lines += f"{when_no_silk} run scoreboard players operation #item_count {ns}.data *= #multiplier {ns}.data"
		lines += f"{when_no_silk} run scoreboard players operation #item_count {ns}.data /= #divider {ns}.data"
	return lines


def write_vanilla_checks(ns: str, unique_blocks: list[str]) -> None:
	""" The block tag of every vanilla block in use, and the predicates telling whether an entity still stands in its own. """
	listed_blocks: list[str] = sorted(x for x in unique_blocks if x != CUSTOM_BLOCK_ALTERNATIVE)
	if "minecraft:cauldron" in listed_blocks:
		listed_blocks.remove("minecraft:cauldron")
		listed_blocks.append("#minecraft:cauldrons")
	Mem.ctx.data[ns].block_tags[VANILLA_BLOCKS_TAG] = set_json_encoder(BlockTag({"values": listed_blocks}))

	pred: JsonDict = loot_condition("minecraft:location_check", predicate={"block": {"blocks": f"#{ns}:{VANILLA_BLOCKS_TAG}"}})
	Mem.ctx.data[ns].predicates["check_vanilla_blocks"] = set_json_encoder(Predicate(pred))

	advanced_predicate: JsonDict = loot_condition("minecraft:any_of", terms=[])
	for block_id in unique_blocks:
		nbt: str = f"{{Tags:[\"{ns}.vanilla.{block_id.replace(':','_')}\"]}}"
		if block_id == CUSTOM_BLOCK_ALTERNATIVE:
			where: JsonDict = {"slots": {"contents":{"predicates":{"minecraft:custom_data": {ns: {"item_frame_destroy": True}}}}}}
		else:
			where = {"location": { "block": { "blocks": "#minecraft:cauldrons" if block_id == "minecraft:cauldron" else block_id }}}
		term: JsonDict = loot_condition("minecraft:entity_properties", entity="this", predicate={"nbt": nbt, **where})
		advanced_predicate["terms"].append(term)
	Mem.ctx.data[ns].predicates["advanced_check_vanilla_blocks"] = set_json_encoder(Predicate(advanced_predicate))


def write_periodic_checks(ns: str, has_growing_seed: bool) -> None:
	""" Look for broken blocks every 2 ticks, every second and every 5 seconds, and refresh the brightness of a sample. """
	ore_block: str = VANILLA_BLOCK_FOR_ORES["id"].replace(':', '_')
	score_check: str = f"score #total_custom_blocks {ns}.data matches 1.."
	write_versioned_function("tick_2", f"""
# 2 ticks destroy detection (item_display only)
execute if {score_check} as @e[type=item_display,tag={ns}.custom_block,tag=!{ns}.vanilla.{ore_block},predicate=!{ns}:check_vanilla_blocks] at @s run function {ns}:custom_blocks/destroy
""")  # noqa: E501
	write_versioned_function("second", f"""
# 1 second break detection (any custom block)
execute if {score_check} as @e[type=#{ns}:custom_blocks,tag={ns}.custom_block,tag=!{ns}.vanilla.{ore_block},predicate=!{ns}:advanced_check_vanilla_blocks] at @s run function {ns}:custom_blocks/destroy
""")  # noqa: E501
	write_versioned_function("second_5", f"""
# 5 seconds break detection (item display only)
execute if {score_check} as @e[type=item_display,tag={ns}.custom_block,predicate=!{ns}:advanced_check_vanilla_blocks] at @s run function {ns}:custom_blocks/destroy
""")  # noqa: E501
	if has_growing_seed:
		write_versioned_function("second_5", f"""
# 5 seconds growing seed break detection (below block check)
execute if score #total_growing_seeds {ns}.data matches 1.. as @e[type=#{ns}:custom_blocks,tag={ns}.growing_seed] at @s run function {ns}:custom_blocks/destroy_growing_seeds
""")  # noqa: E501
	write_versioned_function("second_5", f"""
# 5 seconds dynamic brightness update (random sample of item_display custom blocks)
execute if {score_check} as @e[type=item_display,tag={ns}.custom_block,sort=random,limit=50] at @s run function {ns}:custom_blocks/compute_brightness
""")  # noqa: E501


def write_signal_listeners(ns: str) -> None:
	""" Destroy a block from common_signals: a custom ore's drop, any custom block in place, and an item frame block's drop. """
	if any(data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES for data in Mem.definitions.values()):
		write_function(f"{ns}:calls/common_signals/new_item",
f"""
# If the item is from a custom ore, launch the on_ore_destroyed function
execute if data entity @s Item.components."minecraft:custom_data".common_signals.temp at @s align xyz run function {ns}:calls/common_signals/on_ore_destroyed
""", tags=["common_signals:signals/on_new_item"])  # noqa: E501
		write_function(f"{ns}:calls/common_signals/on_ore_destroyed",
f"""
# Get in a score the item count and if it is a silk touch
scoreboard players set #item_count {ns}.data 0
scoreboard players set #is_silk_touch {ns}.data 0
execute store result score #item_count {ns}.data run data get entity @s Item.count
execute store success score #is_silk_touch {ns}.data if data entity @s Item.components."minecraft:custom_data".common_signals.silk_touch

# Try to destroy the block
function {ns}:calls/common_signals/custom_block_destroy
""")  # noqa: E501

	write_function(
		f"{ns}:calls/common_signals/custom_block_destroy",
		f"execute as @e[tag={ns}.custom_block,dx=0,dy=0,dz=0] at @s run function {ns}:custom_blocks/destroy",
		tags=["common_signals:signals/custom_block_destroy"]
	)

	if not any(data.get(VANILLA_BLOCK, {}).get("contents") for data in Mem.definitions.values()):
		return
	write_function(f"{ns}:calls/common_signals/new_item",
f"""
# If the item is from a custom block alternative, launch the item_frame destroy function
execute if data entity @s Item.components."minecraft:custom_data".{ns}.item_frame_destroy at @s align xyz run function {ns}:calls/common_signals/on_item_frame_destroy
""", tags=["common_signals:signals/on_new_item"])  # noqa: E501
	write_function(f"{ns}:calls/common_signals/on_item_frame_destroy",
f"""
# Try to destroy the block
function {ns}:calls/common_signals/custom_block_destroy

# If still alive, it means that the item_frame has been destroyed too,
execute at @s if entity @s[distance=..1] run function {ns}:calls/common_signals/item_frame_destroy_alt
execute at @s if entity @s[distance=..1] as @n[type=item,nbt={{Item:{{id:"minecraft:item_frame"}}}},distance=..1] run function {ns}:calls/common_signals/item_frame_destroy_alt
""")  # noqa: E501
	write_function(f"{ns}:calls/common_signals/item_frame_destroy_alt", f"""
# Give a new tag to the item frame
data modify storage {ns}:temp Tags set value []
data modify storage {ns}:temp Tags append from entity @s Item.components."minecraft:custom_data".{ns}.alt_destroy
data modify entity @n[type=item,nbt={{Item:{{id:"minecraft:item_frame"}}}},distance=..1] Tags set from storage {ns}:temp Tags

# Remove the custom block "properly"
execute as @n[type=item,nbt={{Item:{{id:"minecraft:item_frame"}}}},distance=..1] run function {ns}:custom_blocks/_groups/{CUSTOM_BLOCK_ALTERNATIVE.replace(':','_')}
""")  # noqa: E501

