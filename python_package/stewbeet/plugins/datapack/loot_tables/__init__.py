
# Imports
import stouputils as stp
from beet import Context, LootTable
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.ingredients import Ingr
from ....core.cls.item import Item
from ....core.cls.resource import Resource
from ....core.constants import ITEMS_LOOT_FOLDER
from ....core.utils.io import write_function


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.datapack.loot_tables'")
def beet_default(ctx: Context):
	""" Main entry point for the loot tables plugin.
	This plugin sets up loot tables for items in the definitions and external items.

	Args:
		ctx (Context): The beet context.
	"""
	# Get data from memory
	Mem.ctx = ctx
	assert ctx.meta["stewbeet"].get("source_lore", None) is not None, "Source lore is not set in the context metadata."
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id

	# Creative loot table (sort of give all loot table)
	creative_loot_table: JsonDict = {"pools": []}
	not_skipped_items: list[str] = [item for item in Mem.definitions.keys() if not Item.from_id(item).skip_gives]

	# For each item in the definitions, create a loot table
	for item in not_skipped_items:
		obj = Item.from_id(item)
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:item",
					"name": obj.base_item
				}]
			}]
		}

		# Set components
		set_components: JsonDict = {
			"function": "minecraft:set_components",
			"components": {}
		}
		for k, v in obj.components.items():
			if k.startswith("!"):
				set_components["components"][f"!minecraft:{k[1:]}"] = {}
			else:
				set_components["components"][f"minecraft:{k}"] = v

		# Add functions
		loot_table["pools"][0]["entries"][0]["functions"] = [set_components]

		# Create loot table with beet
		obj.loot_table.write(LootTable(stp.json_dump(loot_table, max_level = 10)))

		# Add the pool to the creative loot table
		creative_loot_table["pools"].append({"rolls": 1, "entries":[{"type":"minecraft:loot_table","value":obj.loot_table}] })

	# Loot tables for items with crafting recipes
	for item in not_skipped_items:
		obj = Item.from_id(item)
		if obj.recipes:
			results: list[int | JsonDict] = []
			for recipe in obj.recipes:
				# Verify the result is for this item
				if recipe.get("result"):
					result_id = Ingr(recipe["result"]).to_id(add_namespace=False)
					if result_id != item:
						continue

				# Verify count different than 1
				count: int | JsonDict = recipe.get("result_count", 1)
				if count != 1:
					results.append(count)

			# For each result count, create a loot table for it
			for result_count in results:
				loot_table: JsonDict = {
					"pools": [{
						"rolls": 1,
						"entries": [{
							"type": "minecraft:loot_table",
							"value": obj.loot_table,
							"functions": [{
								"function": "minecraft:set_count",
								"count": result_count
							}]
						}]
					}]
				}
				obj.loot_table_for(result_count).write(LootTable(stp.json_dump(loot_table, max_level=10)))

	# Second loot table for the manual (if present)
	if "manual" in not_skipped_items:
		loot_table: JsonDict = {
			"pools": [{
				"rolls": 1,
				"entries": [{
					"type": "minecraft:loot_table",
					"value": Item.from_id("manual").loot_table
				}]
			}]
		}
		# Namespaced alias of the manual loot table, not an item of its own
		Resource(LootTable, f"{ITEMS_LOOT_FOLDER}/{ns}_manual").write(LootTable(stp.json_dump(loot_table, max_level=10)))

	# Write the creative loot table
	if creative_loot_table["pools"]:
		ctx.data[ns].loot_tables["creative_loot_table"] = LootTable(stp.json_dump(creative_loot_table, max_level=2))

	# Make a give all command that gives chests with all the items
	CHEST_SIZE: int = 27
	total_chests: int = (len(not_skipped_items) + CHEST_SIZE - 1) // CHEST_SIZE

	# Get source lore from context metadata
	source_lore: JsonDict = ctx.meta["stewbeet"]["source_lore"]
	lore = stp.json_dump(source_lore, max_level=0).strip()

	chests: list[str] = []
	definitions_copy: list[tuple[str, Item]] = [(item, Item.from_id(item)) for item in not_skipped_items]
	for i in range(total_chests):
		chest_contents: list[str] = []

		# For each slot of the chest, append an item and remove it from the copy
		for j in range(CHEST_SIZE):
			if not definitions_copy:
				break
			item, obj = definitions_copy.pop(0)
			json_content = stp.json_dump(obj.components, max_level=0).strip()
			chest_contents.append(f'{{slot:{j},item:{{count:1,id:"{obj.base_item}",components:{json_content}}}}}')

		joined_content = ",".join(chest_contents)
		chests.append(f'give @s chest[container=[{joined_content}],custom_name={{"text":"Chest [{i+1}/{total_chests}]","color":"yellow"}},lore=[{lore}]]')

	# Write the give all function
	write_function(f"{ns}:_give_all", "\n" + "\n\n".join(chests) + "\n\n")

