
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Advancement
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import Block
from ....core.cls.item import Item
from ....core.constants import (
	BLOCKS_WITH_INTERFACES,
	CUSTOM_BLOCK_ALTERNATIVE,
	CUSTOM_BLOCK_HEAD,
	CUSTOM_BLOCK_HEAD_CUBE_RADIUS,
	CUSTOM_BLOCK_VANILLA,
	GROWING_SEED,
	VANILLA_BLOCK,
)
from ....core.utils.io import set_json_encoder, write_function, write_tag
from ....core.utils.loot_table import advancement_conditions, loot_condition
from ....dependencies.official_libs import OFFICIAL_LIBS, official_lib_used

# Constants
FACING: tuple[str, ...] = ("north", "east", "south", "west")
""" The horizontal directions, in the order the `#rotation` score numbers them from 1. """


# Functions
def write_placement(obj_block: Block, item: str, data: Item) -> tuple[str, str] | None:
	""" Write a custom block's stats line and the functions placing it.

	Returns:
		The vanilla block it stands in and the entity showing it, None when its vanilla block has neither an id nor contents.
	"""
	ns: str = Mem.ctx.project_id
	item_name: str = item.replace("_", " ").title()
	write_function(f"{ns}:_stats_custom_blocks",
		f'tellraw @s [{{"text":"- Total \'{item_name}\': ","color":"gold"}},'
		f'{{"score":{{"name":"#total_{item}","objective":"{ns}.data"}},"color":"yellow"}}]'
	)
	write_function(f"{ns}:_stats_custom_blocks", f'scoreboard players add #total_{item} {ns}.data 0', prepend = True)

	block: JsonDict = data[VANILLA_BLOCK]
	if obj_block.base_item == CUSTOM_BLOCK_ALTERNATIVE:
		write_frame_search(obj_block, item, block)

	# json_dump ends with a newline
	custom_name: str = stp.json_dump({"CustomName": Item.from_id(item).components.get("item_name", item_name)}, max_level=0)[:-1]
	if block.get("id"):
		return write_display_placement(obj_block, item, data, custom_name), "minecraft:item_display"
	if block.get("contents", False):
		write_frame_placement(obj_block, item, data, custom_name)
		return "minecraft:item_frame", "minecraft:item_frame"
	return None


def write_frame_search(obj_block: Block, item: str, block: JsonDict) -> None:
	""" Write the advancement noticing an item frame block placed, and the function finding the frame it became. """
	ns: str = Mem.ctx.project_id
	adv: JsonDict = {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:item_used_on_block",
				"conditions": {
					"location": advancement_conditions([
						loot_condition("minecraft:match_tool", predicate={
							"items": ["minecraft:item_frame"],
							"predicates": {"minecraft:custom_data": {ns: {item: True}}}
						})
					])
				}
			}
		},
		"requirements":[["requirement"]],
		"rewards":{"function": obj_block.functions.search}
	}
	obj_block.alternative_advancement.write(set_json_encoder(Advancement(adv), max_level=-1))

	write_function(obj_block.functions.search, f"""
# Advancement revoke
advancement revoke @s only {obj_block.alternative_advancement}

# Execute the place function as and at the new placed item frame""")
	# Get player rotation if visual_facing is "player" (while @s is still the player)
	if block.get("visual_facing") == "player":
		write_function(obj_block.functions.search, f"function {ns}:custom_blocks/get_rotation")
	if "id" not in block:
		write_function(
			obj_block.functions.search,
			f"execute as @e[type=item_frame,tag={ns}.new,tag={ns}.{item}] at @s "
			f"run function {obj_block.functions.place_main}",
		)
		return

	# A block with an id can only go where there is air, and the item goes back to the player otherwise
	write_function(obj_block.functions.search, f"""tag @s add {ns}.to_refund
execute as @e[type=item_frame,tag={ns}.new,tag={ns}.{item}] at @s run function {obj_block.functions.place_check}
tag @s remove {ns}.to_refund
""")
	write_function(obj_block.functions.place_check, f"""
# Check if there is air block at the position
execute if block ~ ~ ~ air run return run function {obj_block.functions.place_main}

# If not air, give back the item to the player
tag @e[type=item] add {ns}.temp
execute as @p[tag={ns}.to_refund] at @s run loot spawn ~ ~ ~ loot {obj_block.loot_table}
data merge entity @n[type=item,tag=!{ns}.temp] {{PickupDelay:0s,Motion:[0.0d,0.0d,0.0d]}}
data modify entity @n[type=item,tag=!{ns}.temp] Owner set from entity @p[tag={ns}.to_refund] UUID
tag @n[type=item] remove {ns}.temp

# And kill the item frame
kill @s
""")


def write_display_placement(obj_block: Block, item: str, data: Item, custom_name: str) -> str:
	""" Write the place functions of a block shown by an item display inside a vanilla block.

	Returns:
		The vanilla block's id, without its states or data.
	"""
	ns: str = Mem.ctx.project_id
	block: JsonDict = data[VANILLA_BLOCK]
	block_id: str = block["id"].split('[')[0].split('{')[0]
	content: str = f"tag @s add {ns}.placer\n" + setblock_lines(block, custom_name) + (
		"execute align xyz positioned ~0.5 ~0.5 ~0.5 summon item_display at @s "
		f"run function {obj_block.functions.place_secondary}\n"
	) + f"tag @s remove {ns}.placer\n"
	content += f"""
# Increment count scores
scoreboard players add #total_custom_blocks {ns}.data 1
scoreboard players add #total_vanilla_{block_id.replace('minecraft:','')} {ns}.data 1
scoreboard players add #total_{item} {ns}.data 1
{f"scoreboard players add #total_growing_seeds {ns}.data 1" if data.get(GROWING_SEED) else ""}
"""
	if obj_block.base_item == CUSTOM_BLOCK_ALTERNATIVE:
		content += "kill @s[type=item_frame]\n"
	write_function(f"{obj_block.functions.folder}/place_main", content)
	write_function(f"{obj_block.functions.folder}/place_secondary", display_setup(obj_block, item, data, custom_name))
	return block_id


def setblock_lines(block: JsonDict, custom_name: str) -> str:
	""" The commands putting the vanilla block in place, facing the placer when `block_facing` asks for it.

	A block opening an interface is placed with the custom name, which the interface then shows.
	"""
	ns: str = Mem.ctx.project_id
	block_id: str = block["id"]
	beautify_name: str = custom_name if block_id in BLOCKS_WITH_INTERFACES else ""
	if block.get("block_facing") != "player":
		rotation: str = f"function {ns}:custom_blocks/get_rotation\n" if block.get("visual_facing") == "player" else ""
		return rotation + "setblock ~ ~ ~ air strict\n" + f"setblock ~ ~ ~ {block_id}{beautify_name}\n"

	states: str = ""
	if '[' in block_id:
		block_id, states = block_id.split('[')[0], "," + block_id.split('[')[1][:-1]
	return f"function {ns}:custom_blocks/get_rotation\n" + "setblock ~ ~ ~ air strict\n" + "".join(
		f"execute if score #rotation {ns}.data matches {i+1} "
		f"run setblock ~ ~ ~ {block_id}[facing={face}{states}]{beautify_name}\n"
		for i, face in enumerate(FACING)
	)


def display_setup(obj_block: Block, item: str, data: Item, custom_name: str) -> str:
	""" The commands turning a freshly summoned item display into the block, run as that display. """
	ns: str = Mem.ctx.project_id
	block: JsonDict = data[VANILLA_BLOCK]
	block_id: str = block["id"].split('[')[0].split('{')[0].replace(":", "_")

	item_model: str = ""
	if obj_block.components.get("item_model"):
		model_id: str = obj_block.components["item_model"]
		item_model = f"item replace entity @s contents with {CUSTOM_BLOCK_VANILLA}[item_model=\"{model_id}\"]\n"
	content: str = f"""
# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add {ns}.custom_block
tag @s add {ns}.{item}
tag @s add {ns}.vanilla.{block_id}
{f"tag @s add {ns}.growing_seed" if data.get(GROWING_SEED) else ""}

# Add a custom name
data merge entity @s {custom_name}

# Modify item display entity to match the custom block
{item_model}data modify entity @s transformation.scale set value [1.002f,1.002f,1.002f]
function {ns}:custom_blocks/compute_brightness
"""

	if block.get("visual_facing") == "player":
		content += f"""
# Apply rotation
execute if score #rotation {ns}.data matches 1 run data modify entity @s Rotation[0] set value 180.0f
execute if score #rotation {ns}.data matches 2 run data modify entity @s Rotation[0] set value 270.0f
execute if score #rotation {ns}.data matches 3 run data modify entity @s Rotation[0] set value 0.0f
execute if score #rotation {ns}.data matches 4 run data modify entity @s Rotation[0] set value 90.0f
"""

	if OFFICIAL_LIBS["furnace_nbt_recipes"]["is_used"] and block_id.endswith(("_furnace", "_smoker")):
		content += '\n# Furnace NBT Recipes\n'
		content += (
			'execute align xyz positioned ~0.5 ~ ~0.5 '
			'unless entity @e[type=marker,dx=-1,dy=-1,dz=-1,tag=furnace_nbt_recipes.furnace] run '
			'summon marker ~ ~ ~ {Tags:["furnace_nbt_recipes.furnace"]}\n'
		)

	if obj_block.on_place:
		content += f"\n# Custom on_place commands\n{obj_block.on_place}\n"
	return content


def write_frame_placement(obj_block: Block, item: str, data: Item, custom_name: str) -> None:
	""" Write the place functions of a block that is an invisible item frame holding its model. """
	ns: str = Mem.ctx.project_id
	write_function(obj_block.functions.place_main, f"""
# Get the facing direction of the item frame
scoreboard players set #item_frame_facing {ns}.data 1
execute if entity @s[type=item_frame] run function {obj_block.functions.get_facing}

# Summon the new item frame (not execute summon because it would not be invisible for a tick)
summon item_frame ~ ~ ~ {{Tags:["{ns}.new"],Invulnerable:false,Invisible:true,Fixed:false,Silent:true}}
execute as @n[tag={ns}.new] at @s run function {obj_block.functions.place_secondary}

# Increment count scores
scoreboard players add #total_custom_blocks {ns}.data 1
scoreboard players add #total_vanilla_item_frame {ns}.data 1
scoreboard players add #total_{item} {ns}.data 1
{f"scoreboard players add #total_growing_seeds {ns}.data 1" if data.get(GROWING_SEED) else ""}

# Replace the placing sound
playsound minecraft:block.stone.place block @a[distance=..5]
""")
	write_function(obj_block.functions.get_facing, f"""
# Get the facing and delete the old entity
execute store result score #item_frame_facing {ns}.data run data get entity @s Facing
kill @s
""")

	item_model: str = obj_block.components.get("item_model", "minecraft:air")
	content: str = f"""
# Add convention and utils tags, and the custom block tag
tag @s remove {ns}.new
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add {ns}.custom_block
tag @s add {ns}.{item}
tag @s add {ns}.vanilla.minecraft_item_frame
{f"tag @s add {ns}.growing_seed" if data.get(GROWING_SEED) else ""}

# Add a custom name
data merge entity @s {custom_name}

# Modify item frame entity to match the custom block
item replace entity @s contents with {CUSTOM_BLOCK_VANILLA}[item_model="{item_model}",custom_data={{{ns}:{{item_frame_destroy:true,alt_destroy:"{ns}.{item}"}}}}]
execute store result entity @s Facing byte 1 run scoreboard players get #item_frame_facing {ns}.data

# Update position (fixes a Minecraft bug)
execute at @s run tp @s ^ ^ ^0.1
"""  # noqa: E501
	if data[VANILLA_BLOCK].get("visual_facing") == "player":
		content += f"""
# Force ground position
data modify entity @s Facing set value 1b

# Apply rotation based on player direction
execute if score #rotation {ns}.data matches 1 run data modify entity @s ItemRotation set value 4b
execute if score #rotation {ns}.data matches 2 run data modify entity @s ItemRotation set value 6b
execute if score #rotation {ns}.data matches 3 run data modify entity @s ItemRotation set value 0b
execute if score #rotation {ns}.data matches 4 run data modify entity @s ItemRotation set value 2b
"""
	if obj_block.on_place:
		content += f"\n# Custom on_place commands\n{obj_block.on_place}\n"
	write_function(obj_block.functions.place_secondary, content)


def write_smithed_link(ns: str) -> None:
	""" Have smithed's custom block library place the blocks whose item is `CUSTOM_BLOCK_VANILLA`, when there are any. """
	placed_by_smithed: list[str] = [item for item in Mem.definitions if Item.from_id(item).base_item == CUSTOM_BLOCK_VANILLA]
	if not placed_by_smithed:
		return
	if not official_lib_used("smithed.custom_block"):
		stp.debug(
			"Found custom blocks using CUSTOM_BLOCK_VANILLA in the definitions, adding 'smithed.custom_block' to the dependencies"
		)

	write_tag("smithed.custom_block:event/on_place", Mem.ctx.data.function_tags, [f"{ns}:custom_blocks/on_place"])
	write_function(f"{ns}:custom_blocks/on_place", (
		"execute if data storage smithed.custom_block:main blockApi.__data.Items[0].components.\"minecraft:custom_data\".smithed."
		f"block{{from:\"{ns}\"}} run function {ns}:custom_blocks/place\n"
	))
	content: str = f"tag @s add {ns}.placer\n" + "".join(
		f"""execute if data storage smithed.custom_block:main blockApi{{id:"{ns}:{item}"}} """
		f"run function {Block.from_id(item).functions.place_main}\n"
		for item in placed_by_smithed
	) + f"tag @s remove {ns}.placer\n"
	write_function(f"{ns}:custom_blocks/place", content)


def write_head_searches(ns: str) -> None:
	""" For each block placed as a player head, the advancement noticing it and the search finding where it went. """
	for item, data in Mem.definitions.items():
		if Item.from_id(item).base_item == CUSTOM_BLOCK_HEAD and data.get(VANILLA_BLOCK):
			write_head_search(ns, Block.from_id(item), item)


def write_head_search(ns: str, obj_block: Block, item: str) -> None:
	""" Search the cube around the player for the head just placed, one function per axis. """
	adv: JsonDict = {
		"criteria": {
			"requirement": {
				"trigger": "minecraft:placed_block",
				"conditions": {
					"location": advancement_conditions([
						loot_condition("minecraft:location_check", predicate={
							"block": {"predicates": {"minecraft:custom_data": {ns: {item: True}}}}
						})
					])
				}
			}
		},
		"requirements":[["requirement"]],
		"rewards":{"function": obj_block.head_search}
	}
	obj_block.head_advancement.write(set_json_encoder(Advancement(adv), max_level=-1))

	mid_x, mid_y, mid_z = [x // 2 for x in CUSTOM_BLOCK_HEAD_CUBE_RADIUS]
	content: str = "# Search where the head has been placed\n" + "".join(
		f"execute positioned ~{x} ~ ~ run function {obj_block.head_search}_y\n" for x in range(-mid_x, mid_x + 1)
	)
	content += f"\n# Advancement\nadvancement revoke @s only {obj_block.head_advancement}\n\n"
	write_function(obj_block.head_search, content)
	write_function(f"{obj_block.head_search}_y", "# Search y coordinates\n" + "".join(
		f"execute positioned ~ ~{y} ~ run function {obj_block.head_search}_z\n" for y in range(-mid_y, mid_y + 1)
	))
	write_function(f"{obj_block.head_search}_z", "# Search z coordinates\n" + "".join(
		f"execute positioned ~ ~ ~{z} if data block ~ ~ ~ components.\"minecraft:custom_data\".{ns}.{item} "
		f"run function {obj_block.functions.place_main}\n"
		for z in range(-mid_z, mid_z + 1)
	))

