
# Imports
import stouputils as stp

from ...stewbeet.core.constants import NOT_COMPONENTS
from ..utils.io import write_file, write_load_file, write_versioned_function


def main(config: dict):
	version: str = config['version']
	namespace: str = config['namespace']
	major, minor, patch = version.split(".")

	# Setup enumerate and resolve functions
	write_versioned_function(config, "load/enumerate",
f"""
# If current major is too low, set it to the current major
execute unless score #{namespace}.major load.status matches {major}.. run scoreboard players set #{namespace}.major load.status {major}

# If current minor is too low, set it to the current minor (only if major is correct)
execute if score #{namespace}.major load.status matches {major} unless score #{namespace}.minor load.status matches {minor}.. run scoreboard players set #{namespace}.minor load.status {minor}

# If current patch is too low, set it to the current patch (only if major and minor are correct)
execute if score #{namespace}.major load.status matches {major} if score #{namespace}.minor load.status matches {minor} unless score #{namespace}.patch load.status matches {patch}.. run scoreboard players set #{namespace}.patch load.status {patch}
""")
	write_versioned_function(config, "load/resolve",
f"""
# If correct version, load the datapack
execute if score #{namespace}.major load.status matches {major} if score #{namespace}.minor load.status matches {minor} if score #{namespace}.patch load.status matches {patch} run function {namespace}:v{version}/load/main
""")

	# Setup enumerate and resolve function tags
	write_file(f"{config['build_datapack']}/data/{namespace}/tags/function/enumerate.json", stp.super_json_dump({"values": [f"{namespace}:v{version}/load/enumerate"]}))
	write_file(f"{config['build_datapack']}/data/{namespace}/tags/function/resolve.json", stp.super_json_dump({"values": [f"{namespace}:v{version}/load/resolve"]}))

	# Setup load main function
	write_versioned_function(config, "load/main",
f"""
# Avoiding multiple executions of the same load function
execute unless score #{namespace}.loaded load.status matches 1 run function {namespace}:v{version}/load/secondary

""")

	# Confirm load
	items_storage = ""	# Storage representation of every item in the database
	if config['database']:
		items_storage += f"\n# Items storage\ndata modify storage {namespace}:items all set value {{}}\n"
		for item, data in config['database'].items():

			# Prepare storage data with item_model component in first
			mc_data = {"id":"","count":1, "components":{"minecraft:item_model":""}}
			for k, v in data.items():
				if k not in NOT_COMPONENTS:

					# Add 'minecraft:' if missing
					if ":" not in k:
						k = f"minecraft:{k}"

					# Copy component
					mc_data["components"][k] = v

				# Copy the id
				elif k == "id":
					mc_data[k] = v

			# If no item_model, remove it
			if mc_data["components"]["minecraft:item_model"] == "":
				del mc_data["components"]["minecraft:item_model"]

			# Append to the storage database, json_dump adds

			items_storage += f"data modify storage {namespace}:items all.{item} set value " + stp.super_json_dump(mc_data, max_level = 0)

	# Write the loading tellraw and score, along with the final dataset
	write_load_file(config,
f"""
# Confirm load
tellraw @a[tag=convention.debug] {{"text":"[Loaded {config['project_name']} v{version}]","color":"green"}}
scoreboard players set #{namespace}.loaded load.status 1
""" + items_storage)

