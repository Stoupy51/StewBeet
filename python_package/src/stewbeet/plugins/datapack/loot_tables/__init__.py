
# Imports
from beet import Context, LootTable
from beet.core.utils import JsonDict
from stouputils.decorators import measure_time
from stouputils.io import super_json_dump
from stouputils.print import progress

from ....core.__memory__ import Mem
from ....core.constants import NOT_COMPONENTS, RESULT_OF_CRAFTING
from ....core.utils.io import write_function


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.datapack.loot_tables'")
def beet_default(ctx: Context):
	""" Main entry point for the loot tables plugin.
	This plugin sets up loot tables for items in the definitions and external items.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None:
		Mem.ctx = ctx

	# Get data from memory
	assert ctx.meta["stewbeet"].get("source_lore", None) is not None, "Source lore is not set in the context metadata."
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# For each item in the definitions, create a loot table
	for item, data in Mem.definitions.items():
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:item",
					"name": data.get("id")
				}]
			}]
		}

		# Set components
		set_components: JsonDict = {
			"function": "minecraft:set_components",
			"components": {}
		}
		for k, v in data.items():
			if k not in NOT_COMPONENTS:
				set_components["components"][f"minecraft:{k}"] = v

		# Add functions
		loot_table["pools"][0]["entries"][0]["functions"] = [set_components]

		# Create loot table with beet
		ctx.data[ns].loot_tables[f"i/{item}"] = LootTable(super_json_dump(loot_table, max_level = 10))

	# Same for external items
	for item, data in Mem.external_definitions.items():
		ext_ns, item_name = item.split(":")
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:item",
					"name": data.get("id")
				}]
			}]
		}
		set_components: JsonDict = {
			"function": "minecraft:set_components",
			"components": {}
		}
		for k, v in data.items():
			if k not in NOT_COMPONENTS:
				set_components["components"][f"minecraft:{k}"] = v
		loot_table["pools"][0]["entries"][0]["functions"] = [set_components]

		# Create external loot table with beet
		ctx.data[ns].loot_tables[f"external/{ext_ns}/{item_name}"] = LootTable(super_json_dump(loot_table, max_level=10))

	# Loot tables for items with crafting recipes
	for item, data in Mem.definitions.items():
		if data.get(RESULT_OF_CRAFTING):
			results = []
			for d in data[RESULT_OF_CRAFTING]:
				d: dict
				count = d.get("result_count", 1)
				if count != 1:
					results.append(count)

			# For each result count, create a loot table for it
			for result_count in results:
				loot_table: JsonDict = {
					"pools": [{
						"rolls": 1,
						"entries": [{
							"type": "minecraft:loot_table",
							"value": f"{ns}:i/{item}",
							"functions": [{
								"function": "minecraft:set_count",
								"count": result_count
							}]
						}]
					}]
				}
				ctx.data[ns].loot_tables[f"i/{item}_x{result_count}"] = LootTable(super_json_dump(loot_table, max_level=10))

	# Second loot table for the manual (if present)
	if "manual" in Mem.definitions:
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:loot_table",
					"value": f"{ns}:i/manual"
				}]
			}]
		}
		ctx.data[ns].loot_tables[f"i/{ns}_manual"] = LootTable(super_json_dump(loot_table, max_level=10))

	# Make a give all command that gives chests with all the items
	CHEST_SIZE: int = 27
	total_chests: int = (len(Mem.definitions) + CHEST_SIZE - 1) // CHEST_SIZE

	# Get source lore from context metadata
	source_lore: JsonDict = ctx.meta["stewbeet"]["source_lore"]
	lore = super_json_dump(source_lore, max_level=0).strip()

	chests = []
	definitions_copy = list(Mem.definitions.items())
	for i in range(total_chests):
		chest_contents = []

		# For each slot of the chest, append an item and remove it from the copy
		for j in range(CHEST_SIZE):
			if not definitions_copy:
				break
			item, data = definitions_copy.pop(0)
			data = data.copy()
			id = data.get("id")
			for k in NOT_COMPONENTS:	# Remove non-component data
				if data.get(k, None) is not None:
					del data[k]
			json_content = super_json_dump(data, max_level=0).strip()
			chest_contents.append(f'{{slot:{j},item:{{count:1,id:"{id}",components:{json_content}}}}}')

		joined_content = ",".join(chest_contents)
		chests.append(f'give @s chest[container=[{joined_content}],custom_name={{"text":"Chest [{i+1}/{total_chests}]","color":"yellow"}},lore=[{lore}]]')

	# Write the give all function
	write_function(f"{ns}:_give_all", "\n" + "\n\n".join(chests) + "\n\n")

