
# Imports
import stouputils as stp

from ...stewbeet.core.constants import NOT_COMPONENTS, RESULT_OF_CRAFTING
from ..utils.io import write_file, write_function


def main(config: dict):
	database: dict[str,dict] = config["database"]
	external_database: dict[str,dict] = config["external_database"]
	namespace: str = config["namespace"]

	# For each item in the database, create a loot table
	for item, data in database.items():
		loot_table = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:item", "name": data.get("id")}]}]}

		# Set components
		set_components = {"function":"minecraft:set_components","components":{}}
		for k, v in data.items():
			if k not in NOT_COMPONENTS:
				set_components["components"][f"minecraft:{k}"] = v

		# Add functions
		loot_table["pools"][0]["entries"][0]["functions"] = [set_components]

		json_content: str = stp.super_json_dump(loot_table, max_level = 10)
		write_file(f"{config['build_datapack']}/data/{namespace}/loot_table/i/{item}.json", json_content)

	# Same for external items
	for item, data in external_database.items():
		ns, item = item.split(":")
		loot_table = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:item", "name": data.get("id")}]}]}
		set_components = {"function":"minecraft:set_components","components":{}}
		for k, v in data.items():
			if k not in NOT_COMPONENTS:
				set_components["components"][f"minecraft:{k}"] = v
		loot_table["pools"][0]["entries"][0]["functions"] = [set_components]
		write_file(f"{config['build_datapack']}/data/{namespace}/loot_table/external/{ns}/{item}.json", stp.super_json_dump(loot_table, max_level = 9))


	# Loot tables for items with crafting recipes
	for item, data in database.items():
		if data.get(RESULT_OF_CRAFTING):
			results = []
			for d in data[RESULT_OF_CRAFTING]:
				d: dict
				count = d.get("result_count", 1)
				if count != 1:
					results.append(count)

			# For each result count, create a loot table for it
			for result_count in results:
				loot_table = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:loot_table","value":f"{namespace}:i/{item}","functions":[{"function":"minecraft:set_count","count":result_count}]}]}]}
				write_file(f"{config['build_datapack']}/data/{namespace}/loot_table/i/{item}_x{result_count}.json", stp.super_json_dump(loot_table, max_level = -1), overwrite = True)

	# Second loot table for the manual (if present)
	if "manual" in database:
		loot_table = {"pools":[{"rolls":1,"entries":[{"type":"minecraft:loot_table","value":f"{namespace}:i/manual"}]}]}
		write_file(f"{config['build_datapack']}/data/{namespace}/loot_table/i/{namespace}_manual.json", stp.super_json_dump(loot_table, max_level = -1), overwrite = True)

	# Make a give all command that gives chests with all the items
	CHEST_SIZE = 27
	total_chests = (len(database) + CHEST_SIZE - 1) // CHEST_SIZE
	lore = stp.super_json_dump(config["source_lore"], max_level = 0).replace("\n", "")
	chests = []
	database_copy = list(database.items())
	for i in range(total_chests):
		chest_contents = []

		# For each slot of the chest, append an item and remove it from the copy
		for j in range(CHEST_SIZE):
			if not database_copy:
				break
			item, data = database_copy.pop(0)
			data = data.copy()
			id = data.get("id")
			for k in NOT_COMPONENTS:	# Remove non-component data
				if data.get(k, None) is not None:
					del data[k]
			json_content = stp.super_json_dump(data, max_level = 0).replace("\n","")
			chest_contents.append(f'{{slot:{j},item:{{count:1,id:"{id}",components:{json_content}}}}}')
		joined_content = ",".join(chest_contents)
		chests.append(f'give @s chest[container=[{joined_content}],custom_name={{"text":"Chest [{i+1}/{total_chests}]","color":"yellow"}},lore=[{lore}]]')
	write_function(config, f"{namespace}:_give_all", "\n" + "\n\n".join(chests) + "\n\n")

