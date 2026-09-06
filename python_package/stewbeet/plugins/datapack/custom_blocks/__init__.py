
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from pathlib import Path

import stouputils as stp
from beet import Advancement, BlockTag, Context, EntityTypeTag, LootTable, Predicate
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import VANILLA_BLOCK_FOR_ORES, Block, GrowingSeed, GrowingSeedLoot, NoSilkTouchDrop
from ....core.cls.item import Item
from ....core.cls.resource import Resource
from ....core.constants import (
	BLOCKS_WITH_INTERFACES,
	CUSTOM_BLOCK_ALTERNATIVE,
	CUSTOM_BLOCK_HEAD,
	CUSTOM_BLOCK_HEAD_CUBE_RADIUS,
	CUSTOM_BLOCK_VANILLA,
	GROWING_SEED,
	ITEMS_LOOT_FOLDER,
	NO_SILK_TOUCH_DROP,
	VANILLA_BLOCK,
)
from ....core.utils.io import set_json_encoder, write_function, write_load_file, write_tag, write_versioned_function
from ....dependencies.official_libs import OFFICIAL_LIBS, official_lib_used
from ... import sniffer


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.datapack.custom_blocks'")
def beet_default(ctx: Context):
	""" Main entry point for the custom blocks plugin.
	This plugin sets up custom blocks in the datapack based of the given definitions configuration.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx
	ns: str = ctx.project_id
	textures_folder: str = stp.relative_path(ctx.meta.get("stewbeet", {}).get("textures_folder", ""))

	# Assertions
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	assert textures_folder != "", "Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. Please set a directory path in project configuration."

	# Textures
	source_textures: dict[str, str] = {
		stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
		for p in Path(textures_folder).rglob("*.png")
	}

	# Stop if not custom block
	if not any(data.get(VANILLA_BLOCK) for data in Mem.definitions.values()):
		return

	# Predicates
	FACING: list[str] = ["north", "east", "south", "west"]
	for face in FACING:
		pred: JsonDict = {"condition":"minecraft:location_check","predicate":{"block":{"state":{"facing":face}}}}
		ctx.data[ns].predicates[f"facing/{face}"] = set_json_encoder(Predicate(pred))

	# Light level predicates (for dynamic brightness computation)
	for level in range(1, 16):
		light_pred: JsonDict = {"condition": "minecraft:location_check", "predicate": {"light": {"light": level}}}
		ctx.data[ns].predicates[f"light/{level}"] = set_json_encoder(Predicate(light_pred), max_level=-1)

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
		f"execute if score #light {ns}.data matches ..{level - 1} if predicate {ns}:light/{level} run return run scoreboard players set #light {ns}.data {level}\n"
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
	# For each custom block,
	unique_blocks: set[str] = set()
	custom_block_entities: set[str] = set()
	has_growing_seed: bool = False
	for item, data in sniffer.attributed(Mem.definitions.items()):
		obj = Item.from_id(item)
		item_name: str = item.replace("_", " ").title()
		custom_name: str = stp.json_dump({"CustomName": obj.components.get("item_name", item_name)}, max_level=0)[:-1] # Remove the last new line

		# Custom block
		if data.get(VANILLA_BLOCK):
			obj_block = Block.from_id(item)
			block: JsonDict = data[VANILLA_BLOCK]
			path = obj_block.functions.folder

			# Write the line in stats_custom_blocks
			write_function(f"{ns}:_stats_custom_blocks",
				f'tellraw @s [{{"text":"- Total \'{item_name}\': ","color":"gold"}},{{"score":{{"name":"#total_{item}","objective":"{ns}.data"}},"color":"yellow"}}]'
			)
			write_function(f"{ns}:_stats_custom_blocks",
				f'scoreboard players add #total_{item} {ns}.data 0',
				prepend = True
			)

			# If the block is an item frame custom block, make the search function for placement
			if obj_block.base_item == CUSTOM_BLOCK_ALTERNATIVE:

				# Make advancement to detect the item frame placement
				adv: JsonDict = {
					"criteria": {
						"requirement": {
							"trigger": "minecraft:item_used_on_block",
							"conditions": {
								"location": [
									{
										"condition": "minecraft:match_tool",
										"predicate": {
											"items": ["minecraft:item_frame"],
											"predicates": {"minecraft:custom_data": {ns: {item: True}}}
										}
									}
								]
							}
						}
					},
					"requirements":[["requirement"]],
					"rewards":{}
				}
				adv["rewards"]["function"] = obj_block.functions.search
				obj_block.alternative_advancement.write(set_json_encoder(Advancement(adv), max_level=-1))

				# Make search function
				write_function(obj_block.functions.search, f"""
# Advancement revoke
advancement revoke @s only {obj_block.alternative_advancement}

# Execute the place function as and at the new placed item frame""")
				# Get player rotation if visual_facing is "player" (while @s is still the player)
				if block.get("visual_facing") == "player":
					write_function(obj_block.functions.search, f"function {ns}:custom_blocks/get_rotation")
				if "id" not in block:
					write_function(obj_block.functions.search, f"execute as @e[type=item_frame,tag={ns}.new,tag={ns}.{item}] at @s run function {obj_block.functions.place_main}")
				# Make place check function (only if "id" is in VANILLA_BLOCK)
				else:
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

			# If the block is a custom block with a block id,
			if block.get("id"):

				# Get the vanilla block data
				block_id = block["id"]
				beautify_name: str = ""
				if block_id in BLOCKS_WITH_INTERFACES:
					beautify_name = custom_name

				## Place function
				content = ""
				if block.get("block_facing") == "player":
					content += f"function {ns}:custom_blocks/get_rotation\n"
					content += "setblock ~ ~ ~ air strict\n"
					block_states = []
					if '[' in block_id:
						block_states = block_id.split('[')[1][:-1].split(',')
						block_id = block_id.split('[')[0]
					for i, face in enumerate(FACING):
						if block_states:
							content += f"execute if score #rotation {ns}.data matches {i+1} run setblock ~ ~ ~ {block_id}[facing={face}," + ",".join(block_states) + f"]{beautify_name}\n"
						else:
							content += f"execute if score #rotation {ns}.data matches {i+1} run setblock ~ ~ ~ {block_id}[facing={face}]{beautify_name}\n"
				else:
					if block.get("visual_facing") == "player":
						content += f"function {ns}:custom_blocks/get_rotation\n"
					# Simple setblock
					content += "setblock ~ ~ ~ air strict\n"
					content += f"setblock ~ ~ ~ {block_id}{beautify_name}\n"

				# Summon item display and call secondary function
				custom_block_entities.add("minecraft:item_display")  # Add item display entity for custom blocks
				content += f"execute align xyz positioned ~0.5 ~0.5 ~0.5 summon item_display at @s run function {obj_block.functions.place_secondary}\n"

				# Add temporary tags and call main function
				content = f"tag @s add {ns}.placer\n" + content + f"tag @s remove {ns}.placer\n"

				# Increment count scores for stats and optimization
				block_id: str = block_id.split('[')[0].split('{')[0]
				unique_blocks.add(block_id)
				content += f"""
# Increment count scores
scoreboard players add #total_custom_blocks {ns}.data 1
scoreboard players add #total_vanilla_{block_id.replace('minecraft:','')} {ns}.data 1
scoreboard players add #total_{item} {ns}.data 1
{f"scoreboard players add #total_growing_seeds {ns}.data 1" if data.get(GROWING_SEED) else ""}
"""

				# If CUSTOM_BLOCK_ALTERNATIVE, we need to kill the old item frame
				if obj_block.base_item == CUSTOM_BLOCK_ALTERNATIVE:
					content += "kill @s[type=item_frame]\n"

				# Write the file
				write_function(f"{path}/place_main", content)

				## Secondary function
				block_id = block_id.replace(":","_")
				item_model = ""
				if obj_block.components.get("item_model"):
					item_model = f"item replace entity @s contents with {CUSTOM_BLOCK_VANILLA}[item_model=\"{obj_block.components['item_model']}\"]\n"
				content = f"""
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

				# If Furnace NBT Recipes is enabled and the block is a furnace, summon the marker
				if OFFICIAL_LIBS["furnace_nbt_recipes"]["is_used"] and block_id.endswith(("_furnace", "_smoker")):
					content += '\n# Furnace NBT Recipes\n'
					content += (
						'execute align xyz positioned ~0.5 ~ ~0.5 unless entity @e[type=marker,dx=-1,dy=-1,dz=-1,tag=furnace_nbt_recipes.furnace] run '
						'summon marker ~ ~ ~ {Tags:["furnace_nbt_recipes.furnace"]}\n'
					)

				# Append custom on_place commands if defined
				if obj_block.on_place:
					content += f"\n# Custom on_place commands\n{obj_block.on_place}\n"

				# Write file
				write_function(f"{path}/place_secondary", content)

			# If the block is a custom block with "contents", it means it's an item frame not an item display
			elif block.get("contents", False):

				# Write the place main function
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
				# Add the item frame entity to both custom_block_entities and unique_blocks
				custom_block_entities.add("minecraft:item_frame")
				unique_blocks.add("minecraft:item_frame")

				# Secondary function
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
"""
				if block.get("visual_facing") == "player":
					content += f"""
# Force ground position
data modify entity @s Facing set value 1b

# Apply rotation based on player direction
execute if score #rotation {ns}.data matches 1 run data modify entity @s ItemRotation set value 4b
execute if score #rotation {ns}.data matches 2 run data modify entity @s ItemRotation set value 6b
execute if score #rotation {ns}.data matches 3 run data modify entity @s ItemRotation set value 0b
execute if score #rotation {ns}.data matches 4 run data modify entity @s ItemRotation set value 2b
"""

				# Append custom on_place commands if defined
				if obj_block.on_place:
					content += f"\n# Custom on_place commands\n{obj_block.on_place}\n"

				write_function(obj_block.functions.place_secondary, content)
				pass

			# If the block is a growing seed, make the update_seed_model function and call it in the place_secondary function
			if obj_block.growing_seed:
				growing_seed: GrowingSeed = obj_block.growing_seed
				has_growing_seed = True
				write_function(obj_block.functions.place_secondary, f"""
# Update seed model
scoreboard players add @s {ns}.growth_time 0
function {obj_block.functions.update_seed_model}
""")
				# Get the number of growth stages
				texture_basename: str = growing_seed.texture_basename or item
				starts: str = f"{texture_basename}_stage_"
				num_stages: int = len({texture for texture in source_textures if os.path.basename(texture).startswith(starts)})
				progress_stages: int = num_stages - 1 # Last stage is the full grown plant
				growing_time: int = growing_seed.seconds

				# Make the update function
				content: str = ""
				for stage in range(num_stages):
					time_from: int = int(stage * growing_time / progress_stages)
					time_to: int = int((stage + 1) * growing_time / progress_stages) - 1
					time_to_str: str = str(time_to) if stage < progress_stages else ""
					content += (
						f"execute if score @s {ns}.growth_time matches {time_from}..{time_to_str} unless score @s {ns}.growth_stage matches {stage} run "
						f"""function {ns}:custom_blocks/change_seed_stage {{stage:{stage}, model:"{obj_block.seed_stage_item_model(stage)}"}}\n"""
					)
				write_function(obj_block.functions.update_seed_model, f"""
# Update growth stage based on growth_time
{content}
""")
				# Optimisation: If total growing time is higher than 60*stages second, we will increment the growth_time score every minute
				for (speed, secs) in [(60, "minute"), (5, "second_5"), (1, "second")]:
					if growing_time > speed * progress_stages:
						write_function(obj_block.functions[secs], f"""
# Increment growth time score by {speed} and update model
scoreboard players add @s {ns}.growth_time {speed}
execute if score #boost_growth_time {ns}.data matches 1.. run scoreboard players operation @s {ns}.growth_time += #boost_growth_time {ns}.data
function {obj_block.functions.update_seed_model}
""")
						break
				else:
					stp.error(f"Growing seed '{item}' has a growing time < to the number of stages ({growing_time} seconds). Please increase the growing time or reduce the number of stages.")

				# Make the loot table for the seed
				loot_table: str | list[GrowingSeedLoot] = growing_seed.loots
				if not isinstance(loot_table, str):
					obj_block.seed_loot_table.write(set_json_encoder(LootTable({
						"type": "minecraft:block",
						"pools": [
							{
								"rolls": pool.rolls,
								"bonus_rolls": 0,
								"entries": [
									{
										# Vanilla item if "minecraft:" in id,
										# Custom item if plain string
										# Another loot table if ':' in id
										"type": "minecraft:item" if "minecraft:" in pool.id else "minecraft:loot_table",
										# pool.id may name any item, not necessarily one of our own definitions
										"name" if "minecraft:" in pool.id else "value":
											(Resource(LootTable, f"{ITEMS_LOOT_FOLDER}/{pool.id}") if ":" not in pool.id else pool.id),
										**({} if not pool.fortune else {
											"functions": [
												{
													"function": "minecraft:apply_bonus",
													"enchantment": "minecraft:fortune",
													"formula": "minecraft:binomial_with_bonus_count",
													"parameters": pool.fortune,
												},
											]
										})
									}
								]
							}
							for pool in loot_table
						]
					}), max_level=-1))
					loot_table = obj_block.seed_loot_table

				# Make the is_fully_grown function that will be called on destroy
				write_function(obj_block.functions.is_fully_grown, f"""
# If fully grown, drop the loot table and kill the current entity (item)
execute if score #growth_time {ns}.data matches {growing_time}.. as @p[gamemode=!spectator] run loot spawn ~ ~ ~ fish {loot_table} ~ ~ ~ mainhand
execute if score #growth_time {ns}.data matches {growing_time}.. run kill @s
""")
			pass
		pass

	# Make the change_stage function for growing seeds and create scoreboard objectives
	if has_growing_seed:
		write_function(f"{ns}:custom_blocks/change_seed_stage", f"""
# Update the growth stage score
$scoreboard players set @s {ns}.growth_stage $(stage)

# Change the item model to the right stage
$execute if entity @s[type=item_display] run return run data modify entity @s item.components."minecraft:item_model" set value "$(model)"
$execute if entity @s[type=item_frame] run return run data modify entity @s Item.components."minecraft:item_model" set value "$(model)"
""")
		write_load_file(f"""
# Create objectives for growing seeds
scoreboard objectives add {ns}.growth_time dummy
scoreboard objectives add {ns}.growth_stage dummy
""", prepend=True)

	# Link the custom block library to the datapack
	if any(Item.from_id(item).base_item == CUSTOM_BLOCK_VANILLA for item in Mem.definitions.keys()):

		# Change is_used state
		if not official_lib_used("smithed.custom_block"):
			stp.debug("Found custom blocks using CUSTOM_BLOCK_VANILLA in the definitions, adding 'smithed.custom_block' to the dependencies")

		# Write function tag to link with the library
		write_tag("smithed.custom_block:event/on_place", ctx.data.function_tags, [f"{ns}:custom_blocks/on_place"])

		# Write the slot function
		write_function(f"{ns}:custom_blocks/on_place", (
			"execute if data storage smithed.custom_block:main blockApi.__data.Items[0].components.\"minecraft:custom_data\".smithed."
			f"block{{from:\"{ns}\"}} run function {ns}:custom_blocks/place\n"
		))

		# Write the function that will place the custom blocks
		content = f"tag @s add {ns}.placer\n"
		for item in Mem.definitions.keys():
			obj = Item.from_id(item)
			if obj.base_item == CUSTOM_BLOCK_VANILLA:
				place_main = Block.from_id(item).functions.place_main
				content += f"""execute if data storage smithed.custom_block:main blockApi{{id:"{ns}:{item}"}} run function {place_main}\n"""
		content += f"tag @s remove {ns}.placer\n"
		write_function(f"{ns}:custom_blocks/place", content)

	# Sort unique blocks (with custom block alternative last)
	unique_blocks_sorted = sorted(unique_blocks, key=lambda x: (x == CUSTOM_BLOCK_ALTERNATIVE, x))

	## Destroy functions
	# For each unique block, if the vanilla block is missing, call the destroy function for the group
	content = "# Check for missing vanilla blocks\n"
	for block_id in unique_blocks_sorted:
		score_check: str = f"score #total_vanilla_{block_id.replace('minecraft:','')} {ns}.data matches 1.."
		block_underscore = block_id.replace(":","_")

		# Special case for the cauldron that can change block id
		block_id = "#minecraft:cauldrons" if block_id == "minecraft:cauldron" else block_id

		# Add the line that checks if the block is missing
		if block_id != CUSTOM_BLOCK_ALTERNATIVE:
			content += (
				f"execute if {score_check} if entity @s[tag={ns}.vanilla.{block_underscore}] "
				f"unless block ~ ~ ~ {block_id} run return run function {ns}:custom_blocks/_groups/{block_underscore}\n"
			)
		else:
			content += (
				f"execute if {score_check} if entity @s[tag={ns}.vanilla.{block_underscore}] "
				f"unless items entity @s contents *[minecraft:custom_data~{{{ns}:{{item_frame_destroy:true}}}}] run return run function {ns}:custom_blocks/_groups/{block_underscore}\n"
			)
	write_function(f"{ns}:custom_blocks/destroy", content)

	# If there are growing seeds, we need to check the block below to see if it's still valid
	if has_growing_seed:
		content = ""
		for item, data in Mem.definitions.items():
			if data.get(GROWING_SEED):
				growing_seed: GrowingSeed = data[GROWING_SEED]
				planted_on: str = growing_seed.planted_on
				content += (
					f"execute if score #total_{item} {ns}.data matches 1.. if entity @s[tag={ns}.{item}] "
					f"""unless block ~ ~-1 ~ {planted_on} run return run function {ns}:custom_blocks/no_block_below {{item:"{item}"}}\n"""
				)
		write_function(f"{ns}:custom_blocks/destroy_growing_seeds", content)
		write_function(f"{ns}:custom_blocks/no_block_below", f"""
# Break the block we're at and call the destroy function
execute if entity @s[type=item_frame] run summon item ~ ~ ~ {{Item:{{id:"minecraft:item_frame",count:1,components:{{"minecraft:custom_data":{{"{ns}":{{"item_frame_destroy":true}}}}}}}}}}
execute if entity @s[type=item_display] run setblock ~ ~ ~ air destroy
$function {ns}:custom_blocks/$(item)/destroy
""")

	# For each unique block, make the group function
	for block_id in unique_blocks_sorted:

		# Add a line in the stats_custom_blocks file
		score_name: str = f"total_vanilla_{block_id.replace('minecraft:','')}"
		write_function(f"{ns}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- Vanilla \'{block_id}\': ","color":"gray"}},{{"score":{{"name":"#{score_name}","objective":"{ns}.data"}},"color":"white"}}]'
		)
		write_function(f"{ns}:_stats_custom_blocks",
			f'scoreboard players add #{score_name} {ns}.data 0',
			prepend = True
		)

		# Prepare the group function
		block_underscore = block_id.replace(":","_")
		content = "\n"

		# For every custom block, add a tag check for destroy if it's the right vanilla block
		for item, data in Mem.definitions.items():
			if data.get(VANILLA_BLOCK):
				obj_block = Block.from_id(item)

				# Get the vanilla block
				vanilla_block: JsonDict = data[VANILLA_BLOCK]
				if vanilla_block.get("id"):
					this_block = vanilla_block["id"].split('[')[0].split('{')[0]
					this_block = this_block.replace(":","_")
				elif vanilla_block.get("contents", False):
					this_block = CUSTOM_BLOCK_ALTERNATIVE.replace(":","_")
				else:
					continue

				# Add the line if it's the same vanilla block
				if this_block == block_underscore:
					score_check: str = f"score #total_{item} {ns}.data matches 1.."
					content += f"execute if {score_check} if entity @s[tag={ns}.{item}] run function {obj_block.functions.destroy}\n"
		write_function(f"{ns}:custom_blocks/_groups/{block_underscore}", content + "\n")

	# For each custom block, make it's destroy function
	for item, data in Mem.definitions.items():
		if data.get(VANILLA_BLOCK):
			obj_block = Block.from_id(item)
			vanilla_block: JsonDict = data[VANILLA_BLOCK]
			if vanilla_block.get("id"):
				block_id: str = vanilla_block["id"].split('[')[0].split('{')[0]
			elif vanilla_block.get("contents", False):
				block_id = CUSTOM_BLOCK_ALTERNATIVE
			else:
				continue

			# Destroy function
			item_nbt: str = f"""{{id:"{block_id}"}}"""
			if block_id == CUSTOM_BLOCK_ALTERNATIVE:
				item_nbt = f"""{{components:{{"minecraft:custom_data":{{"{ns}":{{"item_frame_destroy":true}}}}}}}}"""
			content = f"""
# Replace the item with the custom one
execute as @n[type=item,nbt={{Item:{item_nbt}}},distance=..1] run function {obj_block.functions.replace_item}
"""
			# If growing seed, get the growth_time score
			if data.get(GROWING_SEED):
				content = content.replace("custom one", f"custom one\nscoreboard players operation #growth_time {ns}.data = @s {ns}.growth_time", 1)

			# Decrease count scores for stats and optimization
			content += f"""
# Decrease count scores
scoreboard players remove #total_custom_blocks {ns}.data 1
scoreboard players remove #total_vanilla_{block_id.replace('minecraft:','')} {ns}.data 1
scoreboard players remove #total_{item} {ns}.data 1
"""

			# Add the destroy function
			write_function(obj_block.functions.destroy, content + "\n# Kill the custom block entity\nkill @s\n")

			# Replace item function
			if not data.get(NO_SILK_TOUCH_DROP):
				content = f"""
# Replace the item with the custom one
data modify entity @s Item.components set from storage {ns}:items all.{item}.components
data modify entity @s Item.id set from storage {ns}:items all.{item}.id
"""
			else:
				# If no VANILLA_BLOCK_FOR_ORES, check if the player has silk touch in mainhand
				if data.get(VANILLA_BLOCK) != VANILLA_BLOCK_FOR_ORES:
					write_function(obj_block.functions.destroy, f"""
# Check if the player has silk touch in mainhand
scoreboard players set #is_silk_touch {ns}.data 0
execute as @p[distance=..10,gamemode=!spectator] if data entity @s SelectedItem.components."minecraft:enchantments"."minecraft:silk_touch" run scoreboard players set #is_silk_touch {ns}.data 1

# If no item found, summon it
execute unless entity @n[type=item,nbt={{Item:{item_nbt}}},distance=..1] run loot spawn ~ ~ ~ loot {{pools:[{{entries:[{{type:"minecraft:item",name:"minecraft:glass"}}],rolls:1}}]}}
""", prepend=True)

				# Handle no silk touch drop
				no_silk_touch_drop: str | JsonDict | NoSilkTouchDrop | LootTable = data[NO_SILK_TOUCH_DROP]
				if isinstance(no_silk_touch_drop, LootTable):
					no_silk_loot_table = obj_block.no_silk_touch_loot_table
					no_silk_loot_table.write(set_json_encoder(no_silk_touch_drop, max_level=-1))
					content = f"""
# If silk touch applied
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.id set from storage {ns}:items all.{item}.id
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.components set from storage {ns}:items all.{item}.components

# Else, no silk touch
execute if score #is_silk_touch {ns}.data matches 0 positioned ~ ~ ~ as @p[distance=..10,gamemode=!spectator] run loot spawn ~ ~ ~ fish {no_silk_loot_table} ~ ~ ~ mainhand
execute if score #is_silk_touch {ns}.data matches 0 unless entity @p[distance=..10,gamemode=!spectator] run loot spawn ~ ~ ~ loot {no_silk_loot_table}
execute if score #is_silk_touch {ns}.data matches 0 run kill @s
"""
					if data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES:
						content += f"""
# Keep item count when silk touch is applied
execute if score #is_silk_touch {ns}.data matches 1 store result entity @s Item.count byte 1 run scoreboard players get #item_count {ns}.data
"""
				else:
					if isinstance(no_silk_touch_drop, dict | NoSilkTouchDrop):
						item_to_drop: str = no_silk_touch_drop["id"]
						if isinstance(no_silk_touch_drop.get("count"), int):
							item_count_min = no_silk_touch_drop["count"]
							item_count_max = no_silk_touch_drop["count"]
						else:
							item_count_min = no_silk_touch_drop["count"]["min"]
							item_count_max = no_silk_touch_drop["count"]["max"]
					else:
						item_to_drop: str = no_silk_touch_drop
						item_count_min: int = 1
						item_count_max: int = 1
					if ':' in item_to_drop:
						silk_text = f'execute if score #is_silk_touch {ns}.data matches 0 run data modify entity @s Item.id set value "{item_to_drop}"'
					else:
						silk_text = (
							f"execute if score #is_silk_touch {ns}.data matches 0 run data modify entity @s Item.id set from storage {ns}:items all.{item_to_drop}.id"
							f"\nexecute if score #is_silk_touch {ns}.data matches 0 run "
							f"data modify entity @s Item.components set from storage {ns}:items all.{item_to_drop}.components"
						)
					if item_count_min == item_count_max and item_count_min != 1:
						silk_text += f"\nexecute if score #is_silk_touch {ns}.data matches 0 run scoreboard players set #multiplier {ns}.data {item_count_min}"
						silk_text += f"\nexecute if score #is_silk_touch {ns}.data matches 0 run scoreboard players operation #item_count {ns}.data *= #multiplier {ns}.data"
					elif item_count_min < item_count_max:
						silk_text += f"\nexecute if score #is_silk_touch {ns}.data matches 0 run scoreboard players set #divider {ns}.data 100"
						silk_text += f"\nexecute if score #is_silk_touch {ns}.data matches 0 store result score #multiplier {ns}.data run random value {item_count_min*100}..{item_count_max*100}"
						silk_text += f"\nexecute if score #is_silk_touch {ns}.data matches 0 run scoreboard players operation #item_count {ns}.data *= #multiplier {ns}.data"
						silk_text += f"\nexecute if score #is_silk_touch {ns}.data matches 0 run scoreboard players operation #item_count {ns}.data /= #divider {ns}.data"
					content = f"""
# If silk touch applied
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.id set from storage {ns}:items all.{item}.id
execute if score #is_silk_touch {ns}.data matches 1 run data modify entity @s Item.components set from storage {ns}:items all.{item}.components

# Else, no silk touch
{silk_text}
"""
					if data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES:
						content += f"""
# Get item count in every case
execute store result entity @s Item.count byte 1 run scoreboard players get #item_count {ns}.data
"""
			# If growing seed, call the loot table function
			if data.get(GROWING_SEED):
				content += f"""
# Check if the seed is fully grown
function {obj_block.functions.is_fully_grown}
"""

			# Write the function
			write_function(obj_block.functions.replace_item, content)


	# Write the used_vanilla_blocks tag, the predicate to check the blocks with the tag and an advanced one
	VANILLA_BLOCKS_TAG = "used_vanilla_blocks"
	listed_blocks = sorted(x for x in unique_blocks_sorted if x != CUSTOM_BLOCK_ALTERNATIVE)
	if "minecraft:cauldron" in listed_blocks:
		listed_blocks.remove("minecraft:cauldron")
		listed_blocks.append("#minecraft:cauldrons")

	# Create block tag
	ctx.data[ns].block_tags[VANILLA_BLOCKS_TAG] = set_json_encoder(BlockTag({"values": listed_blocks}))

	# Create predicate
	pred = {"condition": "minecraft:location_check", "predicate": {"block": {"blocks": f"#{ns}:{VANILLA_BLOCKS_TAG}"}}}
	ctx.data[ns].predicates["check_vanilla_blocks"] = set_json_encoder(Predicate(pred))

	# Create advanced predicate
	advanced_predicate: JsonDict = {"condition": "minecraft:any_of", "terms": []}
	for block_id in unique_blocks_sorted:
		# Replace ":" with "_" for the block name
		block_underscore = block_id.replace(":","_")

		# Special case for cauldron
		if block_id == "minecraft:cauldron":
			block_id = "#minecraft:cauldrons"

		# Create the predicate for the block
		if block_id != CUSTOM_BLOCK_ALTERNATIVE:
			pred = {
				"condition": "minecraft:entity_properties", "entity": "this",
				"predicate": {
					"nbt": f"{{Tags:[\"{ns}.vanilla.{block_underscore}\"]}}",
					"location": { "block": { "blocks": block_id }}
				}
			}
		else:
			pred = {
				"condition": "minecraft:entity_properties", "entity": "this",
				"predicate": {
					"nbt": f"{{Tags:[\"{ns}.vanilla.{block_underscore}\"]}}",
					"slots": {"contents":{"predicates":{"minecraft:custom_data": {ns: {"item_frame_destroy": True}}}}}
				}
			}
		advanced_predicate["terms"].append(pred)
	ctx.data[ns].predicates["advanced_check_vanilla_blocks"] = set_json_encoder(Predicate(advanced_predicate))

	# Write a destroy check every 2 ticks, every second, and every 5 seconds
	ore_block = VANILLA_BLOCK_FOR_ORES["id"].replace(':', '_')
	score_check: str = f"score #total_custom_blocks {ns}.data matches 1.."
	write_versioned_function("tick_2", f"""
# 2 ticks destroy detection (item_display only)
execute if {score_check} as @e[type=item_display,tag={ns}.custom_block,tag=!{ns}.vanilla.{ore_block},predicate=!{ns}:check_vanilla_blocks] at @s run function {ns}:custom_blocks/destroy
""")
	write_versioned_function("second", f"""
# 1 second break detection (any custom block)
execute if {score_check} as @e[type=#{ns}:custom_blocks,tag={ns}.custom_block,tag=!{ns}.vanilla.{ore_block},predicate=!{ns}:advanced_check_vanilla_blocks] at @s run function {ns}:custom_blocks/destroy
""")
	write_versioned_function("second_5", f"""
# 5 seconds break detection (item display only)
execute if {score_check} as @e[type=item_display,tag={ns}.custom_block,predicate=!{ns}:advanced_check_vanilla_blocks] at @s run function {ns}:custom_blocks/destroy
""")
	if has_growing_seed:
		write_versioned_function("second_5", f"""
# 5 seconds growing seed break detection (below block check)
execute if score #total_growing_seeds {ns}.data matches 1.. as @e[type=#{ns}:custom_blocks,tag={ns}.growing_seed] at @s run function {ns}:custom_blocks/destroy_growing_seeds
""")
	write_versioned_function("second_5", f"""
# 5 seconds dynamic brightness update (random sample of item_display custom blocks)
execute if {score_check} as @e[type=item_display,tag={ns}.custom_block,sort=random,limit=50] at @s run function {ns}:custom_blocks/compute_brightness
""")
	# Write the entity type tag for custom blocks
	ctx.data[ns].entity_type_tags["custom_blocks"] = set_json_encoder(EntityTypeTag({"values": sorted(custom_block_entities)}))

	## Custom ores break detection (if any custom ore)
	if any(data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES for data in Mem.definitions.values()):
		write_function(f"{ns}:calls/common_signals/new_item",
f"""
# If the item is from a custom ore, launch the on_ore_destroyed function
execute if data entity @s Item.components."minecraft:custom_data".common_signals.temp at @s align xyz run function {ns}:calls/common_signals/on_ore_destroyed
""", tags=["common_signals:signals/on_new_item"])
		write_function(f"{ns}:calls/common_signals/on_ore_destroyed",
f"""
# Get in a score the item count and if it is a silk touch
scoreboard players set #item_count {ns}.data 0
scoreboard players set #is_silk_touch {ns}.data 0
execute store result score #item_count {ns}.data run data get entity @s Item.count
execute store success score #is_silk_touch {ns}.data if data entity @s Item.components."minecraft:custom_data".common_signals.silk_touch

# Try to destroy the block
function {ns}:calls/common_signals/custom_block_destroy
""")

	# Common signals destroy tag
	write_function(
		f"{ns}:calls/common_signals/custom_block_destroy",
		f"execute as @e[tag={ns}.custom_block,dx=0,dy=0,dz=0] at @s run function {ns}:custom_blocks/destroy",
		tags=["common_signals:signals/custom_block_destroy"]
	)

	## Detect alternative custom blocks destroy
	if any(data.get(VANILLA_BLOCK, {}).get("contents") for data in Mem.definitions.values()):
		write_function(f"{ns}:calls/common_signals/new_item",
f"""
# If the item is from a custom block alternative, launch the item_frame destroy function
execute if data entity @s Item.components."minecraft:custom_data".{ns}.item_frame_destroy at @s align xyz run function {ns}:calls/common_signals/on_item_frame_destroy
""", tags=["common_signals:signals/on_new_item"])
		write_function(f"{ns}:calls/common_signals/on_item_frame_destroy",
f"""
# Try to destroy the block
function {ns}:calls/common_signals/custom_block_destroy

# If still alive, it means that the item_frame has been destroyed too,
execute at @s if entity @s[distance=..1] run function {ns}:calls/common_signals/item_frame_destroy_alt
execute at @s if entity @s[distance=..1] as @n[type=item,nbt={{Item:{{id:"minecraft:item_frame"}}}},distance=..1] run function {ns}:calls/common_signals/item_frame_destroy_alt
""")
		write_function(f"{ns}:calls/common_signals/item_frame_destroy_alt", f"""
# Give a new tag to the item frame
data modify storage {ns}:temp Tags set value []
data modify storage {ns}:temp Tags append from entity @s Item.components."minecraft:custom_data".{ns}.alt_destroy
data modify entity @n[type=item,nbt={{Item:{{id:"minecraft:item_frame"}}}},distance=..1] Tags set from storage {ns}:temp Tags

# Remove the custom block "properly"
execute as @n[type=item,nbt={{Item:{{id:"minecraft:item_frame"}}}},distance=..1] run function {ns}:custom_blocks/_groups/{CUSTOM_BLOCK_ALTERNATIVE.replace(':','_')}
""")

	# Add line in the stats_custom_blocks file
	write_function(f"{ns}:_stats_custom_blocks",
		f'tellraw @s [{{"text":"- Total custom blocks: ","color":"dark_aqua"}},{{"score":{{"name":"#total_custom_blocks","objective":"{ns}.data"}},"color":"aqua"}}]'
	)
	write_function(f"{ns}:_stats_custom_blocks",
		f'scoreboard players add #total_custom_blocks {ns}.data 0',
		prepend = True
	)
	if has_growing_seed:
		write_function(f"{ns}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- Total growing seeds: ","color":"dark_aqua"}},{{"score":{{"name":"#total_growing_seeds","objective":"{ns}.data"}},"color":"aqua"}}]'
		)
		write_function(f"{ns}:_stats_custom_blocks",
			f'scoreboard players add #total_growing_seeds {ns}.data 0',
			prepend = True
		)



	## Custom blocks using player_head
	for item, data in Mem.definitions.items():
		obj = Item.from_id(item)
		if obj.base_item == CUSTOM_BLOCK_HEAD and data.get(VANILLA_BLOCK):
			obj_block = Block.from_id(item)

			# Make advancement
			adv: JsonDict = {
				"criteria": {
					"requirement": {
						"trigger": "minecraft:placed_block",
						"conditions": {
							"location": [
								{
									"condition": "minecraft:location_check",
									"predicate": {
										"block": {"predicates": {"minecraft:custom_data": {ns: {item: True}}}}
									}
								}
							]
						}
					}
				},
				"requirements":[["requirement"]],
				"rewards":{}
			}
			adv["rewards"]["function"] = obj_block.head_search
			obj_block.head_advancement.write(set_json_encoder(Advancement(adv), max_level=-1))

			## Make search function
			content = "# Search where the head has been placed\n"
			mid_x, mid_y, mid_z = [x // 2 for x in CUSTOM_BLOCK_HEAD_CUBE_RADIUS]

			# Generate main search function that calls x-loop
			for x in range(-mid_x, mid_x + 1):
				content += f"execute positioned ~{x} ~ ~ run function {obj_block.head_search}_y\n"
			content += f"\n# Advancement\nadvancement revoke @s only {obj_block.head_advancement}\n\n"
			write_function(obj_block.head_search, content)

			# Generate y-loop function
			content_y = "# Search y coordinates\n"
			for y in range(-mid_y, mid_y + 1):
				content_y += f"execute positioned ~ ~{y} ~ run function {obj_block.head_search}_z\n"
			write_function(f"{obj_block.head_search}_y", content_y)

			# Generate z-loop function
			content_z = "# Search z coordinates\n"
			for z in range(-mid_z, mid_z + 1):
				content_z += f"execute positioned ~ ~ ~{z} if data block ~ ~ ~ components.\"minecraft:custom_data\".{ns}.{item} run function {obj_block.functions.place_main}\n"
			write_function(f"{obj_block.head_search}_z", content_z)

