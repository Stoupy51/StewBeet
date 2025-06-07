
# Imports
from typing import Any

import stouputils as stp

from ...stewbeet.core.constants import (
	BLOCKS_WITH_INTERFACES,
	CUSTOM_BLOCK_HEAD,
	CUSTOM_BLOCK_HEAD_CUBE_RADIUS,
	CUSTOM_BLOCK_VANILLA,
	NO_SILK_TOUCH_DROP,
	OFFICIAL_LIBS,
	VANILLA_BLOCK,
	VANILLA_BLOCK_FOR_ORES,
	official_lib_used,
)
from ..utils.io import write_file, write_function, write_versioned_function


def main(config: dict):
	namespace: str = config['namespace']
	build_datapack: str = config['build_datapack']
	database: dict = config['database']

	# Stop if not custom block
	if not any(data.get(VANILLA_BLOCK) for data in database.values()):
		return

	# Predicates
	FACING = ["north", "east", "south", "west"]
	for face in FACING:
		predicate = {"condition":"minecraft:location_check","predicate":{"block":{"state":{"facing":face}}}}
		write_file(f"{build_datapack}/data/{namespace}/predicate/facing/{face}.json", stp.super_json_dump(predicate))

	# Get rotation function
	write_function(config, f"{namespace}:custom_blocks/get_rotation",
f"""
# Set up score
scoreboard players set #rotation {namespace}.data 0

# Player case
execute if score #rotation {namespace}.data matches 0 if entity @s[y_rotation=-46..45] run scoreboard players set #rotation {namespace}.data 1
execute if score #rotation {namespace}.data matches 0 if entity @s[y_rotation=45..135] run scoreboard players set #rotation {namespace}.data 2
execute if score #rotation {namespace}.data matches 0 if entity @s[y_rotation=135..225] run scoreboard players set #rotation {namespace}.data 3
execute if score #rotation {namespace}.data matches 0 if entity @s[y_rotation=225..315] run scoreboard players set #rotation {namespace}.data 4

# Predicate case
execute if score #rotation {namespace}.data matches 0 if predicate {namespace}:facing/north run scoreboard players set #rotation {namespace}.data 1
execute if score #rotation {namespace}.data matches 0 if predicate {namespace}:facing/east run scoreboard players set #rotation {namespace}.data 2
execute if score #rotation {namespace}.data matches 0 if predicate {namespace}:facing/south run scoreboard players set #rotation {namespace}.data 3
execute if score #rotation {namespace}.data matches 0 if predicate {namespace}:facing/west run scoreboard players set #rotation {namespace}.data 4
# No more cases for now
""")

	# For each custom block,
	unique_blocks = set()
	for item, data in database.items():
		item: str
		data: dict[str, Any]
		item_name: str = item.replace("_", " ").title()
		custom_name: str = stp.super_json_dump({"CustomName": data.get("item_name", item_name)}, max_level = 0)

		# Custom block
		if data.get(VANILLA_BLOCK):
			block = data[VANILLA_BLOCK]
			block_id = block["id"]
			path = f"{namespace}:custom_blocks/{item}"
			beautify_name: str = ""
			if block_id in BLOCKS_WITH_INTERFACES:
				beautify_name = custom_name

			## Place function
			content = ""
			if block["apply_facing"]:
				content += f"function {namespace}:custom_blocks/get_rotation\n"
				content += "setblock ~ ~ ~ air\n"
				block_states = []
				if '[' in block_id:
					block_states = block_id.split('[')[1][:-1].split(',')
					block_id = block_id.split('[')[0]
				for i, face in enumerate(FACING):
					if block_states:
						content += f"execute if score #rotation {namespace}.data matches {i+1} run setblock ~ ~ ~ {block_id}[facing={face}," + ",".join(block_states) + f"]{beautify_name}\n"
					else:
						content += f"execute if score #rotation {namespace}.data matches {i+1} run setblock ~ ~ ~ {block_id}[facing={face}]{beautify_name}\n"
			else:
				# Simple setblock
				content += "setblock ~ ~ ~ air\n"
				content += f"setblock ~ ~ ~ {block_id}{beautify_name}\n"

			# Summon item display and call secondary function
			content += f"execute align xyz positioned ~.5 ~.5 ~.5 summon item_display at @s run function {namespace}:custom_blocks/{item}/place_secondary\n"

			# Add temporary tags and call main function
			content = f"tag @s add {namespace}.placer\n" + content + f"tag @s remove {namespace}.placer\n"

			# Increment count scores for stats and optimization
			block_id: str = block_id.split('[')[0].split('{')[0]
			unique_blocks.add(block_id)
			content += f"""
# Increment count scores
scoreboard players add #total_custom_blocks {namespace}.data 1
scoreboard players add #total_vanilla_{block_id.replace('minecraft:','')} {namespace}.data 1
scoreboard players add #total_{item} {namespace}.data 1
"""

			# Write the file
			write_function(config, f"{path}/place_main", content)

			# Write the line in stats_custom_blocks
			write_function(config, f"{namespace}:_stats_custom_blocks",
				f'tellraw @s [{{"text":"- Total \'{item_name}\': ","color":"gold"}},{{"score":{{"name":"#total_{item}","objective":"{namespace}.data"}},"color":"yellow"}}]\n'
			)
			write_function(config, f"{namespace}:_stats_custom_blocks",
				f'scoreboard players add #total_{item} {namespace}.data 0\n',
				prepend = True
			)

			## Secondary function
			block_id = block_id.replace(":","_")
			set_custom_model = ""
			if data.get("item_model"):
				set_custom_model = f"item replace entity @s container.0 with {CUSTOM_BLOCK_VANILLA}[item_model=\"{data['item_model']}\"]\n"
			content = f"""
# Add convention and utils tags, and the custom block tag
tag @s add global.ignore
tag @s add global.ignore.kill
tag @s add smithed.entity
tag @s add smithed.block
tag @s add {namespace}.custom_block
tag @s add {namespace}.{item}
tag @s add {namespace}.vanilla.{block_id}

# Add a custom name
data merge entity @s {custom_name}

# Modify item display entity to match the custom block
{set_custom_model}data modify entity @s transformation.scale set value [1.002f,1.002f,1.002f]
data modify entity @s brightness set value {{block:15,sky:15}}
"""
			if block["apply_facing"]:
				content += f"""
# Apply rotation
execute if score #rotation {namespace}.data matches 1 run data modify entity @s Rotation[0] set value 180.0f
execute if score #rotation {namespace}.data matches 2 run data modify entity @s Rotation[0] set value 270.0f
execute if score #rotation {namespace}.data matches 3 run data modify entity @s Rotation[0] set value 0.0f
execute if score #rotation {namespace}.data matches 4 run data modify entity @s Rotation[0] set value 90.0f
"""

			# If Furnace NBT Recipes is enabled and the block is a furnace, summon the marker
			if OFFICIAL_LIBS["furnace_nbt_recipes"]["is_used"] and block_id.endswith(("_furnace", "_smoker")):
				content += '\n# Furnace NBT Recipes\n'
				content += 'execute align xyz positioned ~.5 ~ ~.5 unless entity @e[type=marker,dx=-1,dy=-1,dz=-1,tag=furnace_nbt_recipes.furnace] run summon marker ~ ~ ~ {Tags:["furnace_nbt_recipes.furnace"]}\n'

			# Write file
			write_function(config, f"{path}/place_secondary", content)
		pass

	# Link the custom block library to the datapack
	smithed_custom_blocks = [1 for data in database.values() if data.get("id") == CUSTOM_BLOCK_VANILLA]
	if smithed_custom_blocks:

		# Change is_used state
		if not official_lib_used("smithed.custom_block"):
			stp.debug("Found custom blocks using CUSTOM_BLOCK_VANILLA in the database, adding 'smithed.custom_block' to the dependencies")

		# Write function tag to link with the library
		write_file(f"{build_datapack}/data/smithed.custom_block/tags/function/event/on_place.json", stp.super_json_dump({"values": [f"{namespace}:custom_blocks/on_place"]}))

		# Write the slot function
		write_function(config, f"{namespace}:custom_blocks/on_place", f"execute if data storage smithed.custom_block:main blockApi.__data.Items[0].components.\"minecraft:custom_data\".smithed.block{{from:\"{namespace}\"}} run function {namespace}:custom_blocks/place\n")

		# Write the function that will place the custom blocks
		content = f"tag @s add {namespace}.placer\n"
		for item, data in database.items():
			if data.get("id") == CUSTOM_BLOCK_VANILLA:
				content += f"execute if data storage smithed.custom_block:main blockApi{{id:\"{namespace}:{item}\"}} run function {namespace}:custom_blocks/{item}/place_main\n"
		content += f"tag @s remove {namespace}.placer\n"
		write_function(config, f"{namespace}:custom_blocks/place", content)

	# Sort unique blocks
	unique_blocks = sorted(list(unique_blocks))

	## Destroy functions
	# For each unique block, if the vanilla block is missing, call the destroy function for the group
	content = "\n"
	for block_id in unique_blocks:
		score_check: str = f"score #total_vanilla_{block_id.replace('minecraft:','')} {namespace}.data matches 1.."
		block_underscore = block_id.replace(":","_")
		block_id = "#minecraft:cauldrons" if block_id == "minecraft:cauldron" else block_id
		content += f"execute if {score_check} if entity @s[tag={namespace}.vanilla.{block_underscore}] unless block ~ ~ ~ {block_id} run function {namespace}:custom_blocks/_groups/{block_underscore}\n"
	write_function(config, f"{namespace}:custom_blocks/destroy", content + "\n")

	# For each unique block, make the group function
	for block_id in unique_blocks:

		# Add a line in the stats_custom_blocks file
		score_name: str = f"total_vanilla_{block_id.replace('minecraft:','')}"
		write_function(config, f"{namespace}:_stats_custom_blocks",
			f'tellraw @s [{{"text":"- Vanilla \'{block_id}\': ","color":"gray"}},{{"score":{{"name":"#{score_name}","objective":"{namespace}.data"}},"color":"white"}}]\n'
		)
		write_function(config, f"{namespace}:_stats_custom_blocks",
			f'scoreboard players add #{score_name} {namespace}.data 0\n',
			prepend = True
		)

		# Prepare the group function
		block_underscore = block_id.replace(":","_")
		content = "\n"

		# For every custom block, add a tag check for destroy if it's the right vanilla block
		for item, data in database.items():
			if data.get(VANILLA_BLOCK):

				# Get the vanilla block
				this_block = data[VANILLA_BLOCK]["id"].split('[')[0].split('{')[0]
				this_block = this_block.replace(":","_")

				# Add the line if it's the same vanilla block
				if this_block == block_underscore:
					score_check: str = f"score #total_{item} {namespace}.data matches 1.."
					content += f"execute if {score_check} if entity @s[tag={namespace}.{item}] run function {namespace}:custom_blocks/{item}/destroy\n"
		write_function(config, f"{namespace}:custom_blocks/_groups/{block_underscore}", content + "\n")

	# For each custom block, make it's destroy function
	for item, data in database.items():
		if data.get(VANILLA_BLOCK):
			block = data[VANILLA_BLOCK]
			path = f"{namespace}:custom_blocks/{item}"
			block_id: str = block["id"].split('[')[0].split('{')[0]

			# Destroy function
			content = f"""
# Replace the item with the custom one
execute as @n[type=item,nbt={{Item:{{id:"{block_id}"}}}},distance=..1] run function {namespace}:custom_blocks/{item}/replace_item
"""

			# Decrease count scores for stats and optimization
			content += f"""
# Decrease count scores
scoreboard players remove #total_custom_blocks {namespace}.data 1
scoreboard players remove #total_vanilla_{block_id.replace('minecraft:','')} {namespace}.data 1
scoreboard players remove #total_{item} {namespace}.data 1
"""

			# Add the destroy function
			write_function(config, f"{path}/destroy", content + "\n# Kill the custom block entity\nkill @s\n\n")

			# Replace item function
			if block != VANILLA_BLOCK_FOR_ORES:
				content = f"""
data modify entity @s Item.components set from storage {namespace}:items all.{item}.components
data modify entity @s Item.id set from storage {namespace}:items all.{item}.id
"""
			else:
				no_silk_touch_drop = data[NO_SILK_TOUCH_DROP]
				if ':' in no_silk_touch_drop:
					silk_text = f'execute if score #is_silk_touch {config["namespace"]}.data matches 0 run data modify entity @s Item.id set value "{no_silk_touch_drop}"'
				else:
					silk_text = f"execute if score #is_silk_touch {namespace}.data matches 0 run data modify entity @s Item.id set from storage {namespace}:items all.{no_silk_touch_drop}.id"
					silk_text += f"\nexecute if score #is_silk_touch {namespace}.data matches 0 run data modify entity @s Item.components set from storage {namespace}:items all.{no_silk_touch_drop}.components"
				content = f"""
# If silk touch applied
execute if score #is_silk_touch {namespace}.data matches 1 run data modify entity @s Item.id set from storage {namespace}:items all.{item}.id
execute if score #is_silk_touch {namespace}.data matches 1 run data modify entity @s Item.components set from storage {namespace}:items all.{item}.components

# Else, no silk touch
{silk_text}

# Get item count in every case
execute store result entity @s Item.count byte 1 run scoreboard players get #item_count {namespace}.data
"""
			write_function(config, f"{path}/replace_item", content)


	# Write the used_vanilla_blocks tag, the predicate to check the blocks with the tag and an advanced one
	VANILLA_BLOCKS_TAG = "used_vanilla_blocks"
	listed_blocks = list(unique_blocks)
	if "minecraft:cauldron" in listed_blocks:
		listed_blocks.remove("minecraft:cauldron")
		listed_blocks.append("#minecraft:cauldrons")
	write_file(f"{build_datapack}/data/{namespace}/tags/block/{VANILLA_BLOCKS_TAG}.json", stp.super_json_dump({"values": listed_blocks}))
	predicate = {"condition": "minecraft:location_check", "predicate": {"block": {"blocks": f"#{namespace}:{VANILLA_BLOCKS_TAG}"}}}
	write_file(f"{build_datapack}/data/{namespace}/predicate/check_vanilla_blocks.json", stp.super_json_dump(predicate))
	advanced_predicate = {"condition": "minecraft:any_of", "terms": []}
	for block in unique_blocks:
		block_underscore = block.replace(":","_")
		if block == "minecraft:cauldron":
			block = "#minecraft:cauldrons"
		predicate = {"condition": "minecraft:entity_properties", "entity": "this", "predicate": { "nbt": f"{{Tags:[\"{namespace}.vanilla.{block_underscore}\"]}}", "location": { "block": { "blocks": block }}}}
		advanced_predicate["terms"].append(predicate)
	write_file(f"{build_datapack}/data/{namespace}/predicate/advanced_check_vanilla_blocks.json", stp.super_json_dump(advanced_predicate))

	# Write a destroy check every 2 ticks, every second, and every 5 seconds
	ore_vanilla_block = VANILLA_BLOCK_FOR_ORES["id"].replace(':', '_')
	score_check: str = f"score #total_custom_blocks {namespace}.data matches 1.."
	write_versioned_function(config, "tick_2",
f"""
# 2 ticks destroy detection
execute if {score_check} as @e[type=item_display,tag={namespace}.custom_block,tag=!{namespace}.vanilla.{ore_vanilla_block},predicate=!{namespace}:check_vanilla_blocks] at @s run function {namespace}:custom_blocks/destroy
""")
	write_versioned_function(config, "second",
f"""
# 1 second break detection
execute if {score_check} as @e[type=item_display,tag={namespace}.custom_block,tag=!{namespace}.vanilla.{ore_vanilla_block},predicate=!{namespace}:advanced_check_vanilla_blocks] at @s run function {namespace}:custom_blocks/destroy
""")
	write_versioned_function(config, "second_5",
f"""
# 5 seconds break detection
execute if {score_check} as @e[type=item_display,tag={namespace}.custom_block,predicate=!{namespace}:advanced_check_vanilla_blocks] at @s run function {namespace}:custom_blocks/destroy
""")



	## Custom ores break detection (if any custom ore)
	if any(data.get(VANILLA_BLOCK) == VANILLA_BLOCK_FOR_ORES for data in database.values()):
		write_file(f"{build_datapack}/data/common_signals/tags/function/signals/on_new_item.json", stp.super_json_dump({"values": [f"{namespace}:calls/common_signals/new_item"]}))
		write_function(config, f"{namespace}:calls/common_signals/new_item",
f"""
# If the item is from a custom ore, launch the on_ore_destroyed function
execute if data entity @s Item.components.\"minecraft:custom_data\".common_signals.temp at @s align xyz run function {namespace}:calls/common_signals/on_ore_destroyed
""")
		write_function(config, f"{namespace}:calls/common_signals/on_ore_destroyed",
f"""
# Get in a score the item count and if it is a silk touch
scoreboard players set #item_count {namespace}.data 0
scoreboard players set #is_silk_touch {namespace}.data 0
execute store result score #item_count {namespace}.data run data get entity @s Item.count
execute store success score #is_silk_touch {namespace}.data if data entity @s Item.components."minecraft:custom_data".common_signals.silk_touch

# Try to destroy the block
execute as @e[tag={namespace}.custom_block,dx=0,dy=0,dz=0] at @s run function {namespace}:custom_blocks/destroy
""")


	# Add line in the stats_custom_blocks file
	write_function(config, f"{namespace}:_stats_custom_blocks",
		f'tellraw @s [{{"text":"- Total custom blocks: ","color":"dark_aqua"}},{{"score":{{"name":"#total_custom_blocks","objective":"{namespace}.data"}},"color":"aqua"}}]\n'
	)
	write_function(config, f"{namespace}:_stats_custom_blocks",
		f'scoreboard players add #total_custom_blocks {namespace}.data 0\n',
		prepend = True
	)


	## Custom blocks using player_head
	for item, data in database.items():
		if data["id"] == CUSTOM_BLOCK_HEAD and data.get(VANILLA_BLOCK):

			# Make advancement
			predicate = {"criteria":{"requirement":{"trigger":"minecraft:placed_block","conditions":{"location": [{"condition": "minecraft:location_check","predicate": {"block": {}}}]}}},"requirements":[["requirement"]],"rewards":{}}
			predicate["criteria"]["requirement"]["conditions"]["location"][0]["predicate"]["block"]["nbt"] = stp.super_json_dump({"components":{"minecraft:custom_data":data.get("custom_data", {})}}, max_level = 0)
			predicate["rewards"]["function"] = f"{namespace}:custom_blocks/_player_head/search_{item}"
			write_file(f"{build_datapack}/data/{namespace}/advancement/custom_block_head/{item}.json", stp.super_json_dump(predicate, max_level = -1))

			# Make search function
			content = "# Search where the head has been placed\n"
			mid_x, mid_y, mid_z = [x // 2 for x in CUSTOM_BLOCK_HEAD_CUBE_RADIUS]
			for x in range(-mid_x, mid_x + 1):
				for y in range(-mid_y, mid_y + 1):
					for z in range(-mid_z, mid_z + 1):
						content += f"execute positioned ~{x} ~{y} ~{z} if data block ~ ~ ~ components.\"minecraft:custom_data\".{namespace}.{item} run function {namespace}:custom_blocks/{item}/place_main\n"
			content += f"\n# Advancement\nadvancement revoke @s only {namespace}:custom_block_head/{item}\n\n"
			write_function(config, f"{namespace}:custom_blocks/_player_head/search_{item}", content)

