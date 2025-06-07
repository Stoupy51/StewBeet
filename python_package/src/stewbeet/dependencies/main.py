
# Imports
import stouputils as stp

from ...stewbeet.core.constants import *
from ..utils.io import *

# This folder path
OFFICIAL_LIBS_PATH: str = stp.get_root_path(__file__)

# Util function for checking version
def check_version(config: dict, lib_ns: str, data: dict, run_command: str) -> str:
	ns: str = config['namespace']
	checks: str = ""
	major, minor, patch = data["version"]
	score_major: str = f"score #{lib_ns}.major load.status matches {major}"
	score_minor: str = f"score #{lib_ns}.minor load.status matches {minor}"
	score_patch: str = f"score #{lib_ns}.patch load.status matches {patch}" if patch > 0 else ""

	# If bookshelf, replace #bs by $bs
	if lib_ns.startswith("bs."):
		score_major = score_major.replace("#", "$")
		score_minor = score_minor.replace("#", "$")
		score_patch = score_patch.replace("#", "$")

	# Check if the version is correct
	is_decoder: int = 1 if "tellraw @" in run_command else 0
	checks += f"execute if score #dependency_error {ns}.data matches {is_decoder} unless {score_major}.. run {run_command}\n"
	checks += f"execute if score #dependency_error {ns}.data matches {is_decoder} if {score_major} unless {score_minor}.. run {run_command}\n"
	if score_patch:
		checks += f"execute if score #dependency_error {ns}.data matches {is_decoder} if {score_major} if {score_minor} unless {score_patch}.. run {run_command}\n"
	return checks

# Main function called on finalization process
def main(config: dict) -> None:
	ns: str = config["namespace"]
	version: str = config["version"]
	major, minor, patch = version.split(".")

	# Find if common_signals is used
	if ns != "common_signals":
		for file_content in FILES_TO_WRITE.values():
			if "common_signals" in file_content:
				if not official_lib_used("common_signals"):
					stp.debug("Found the use of official supported library 'common_signals', adding it to the datapack")
				break

	# Find if itemio is used
	if ns != "itemio":
		for file_content in FILES_TO_WRITE.values():
			if "itemio" in file_content:
				if not official_lib_used("itemio"):
					stp.debug("Found the use of official supported library 'itemio', adding it to the datapack")
				break

	# Find for each bookshelf module if it is used
	if ns != "bookshelf":
		for module_ns in BOOKSHELF_MODULES.keys():
			for file_content in FILES_TO_WRITE.values():
				if f"#{module_ns}:" in file_content:
					if not official_lib_used(module_ns):
						stp.debug(f"Found the use of official supported library '{module_ns}', adding it to the datapack")
					break

	# Get all dependencies (official and custom)
	dependencies: list[tuple[str, dict]] = [(ns, data) for ns, data in OFFICIAL_LIBS.items() if data["is_used"]]
	if config.get("dependencies"):
		dependencies += list(config['dependencies'].items())

	# Setup Lantern Load
	write_file(f"{config['build_datapack']}/data/minecraft/tags/function/load.json", stp.super_json_dump({"values": ["#load:_private/load"]}))
	write_file(f"{config['build_datapack']}/data/load/tags/function/_private/init.json", stp.super_json_dump({"values": ["load:_private/init"]}))
	write_file(f"{config['build_datapack']}/data/load/tags/function/_private/load.json", stp.super_json_dump(
		{"values": ["#load:_private/init",{"id":"#load:pre_load","required":False},{"id":"#load:load","required":False},{"id":"#load:post_load","required":False}]}
	))
	write_function(config, "load:_private/init", """
# Reset scoreboards so packs can set values accurate for current load.
scoreboard objectives add load.status dummy
scoreboard players reset * load.status
""")


	# Setup load json files
	write_file(f"{config['build_datapack']}/data/load/tags/function/load.json", stp.super_json_dump({"values": [f"#{ns}:load"]}))
	values: list[str | dict] = [f"#{ns}:enumerate", f"#{ns}:resolve"]
	if dependencies:
		enum_tag: dict = json.loads(read_tags(config, f"{ns}:function/enumerate"))
		enum_tag["values"].insert(0, f"#{ns}:dependencies")
		write_tags(config, f"{ns}:function/enumerate", stp.super_json_dump(enum_tag), overwrite=True)
	write_file(f"{config['build_datapack']}/data/{ns}/tags/function/load.json", stp.super_json_dump({"values": values}, max_level = 3))
	if dependencies:
		calls = [{"id":f"#{ns}:load" if not ns.startswith("bs.") else "#bs.load:load", "required": False} for ns, _ in dependencies]
		calls = stp.unique_list(calls)
		write_file(f"{config['build_datapack']}/data/{ns}/tags/function/dependencies.json", stp.super_json_dump({"values": calls}))

	# Write secondary function
	authors = config["author"].replace(",", " ").replace("  ", " ").split(" ")
	convention_debug = "".join([f"tag {author} add convention.debug\n" for author in authors])
	content = f"""
# {config['project_name']}
scoreboard objectives add {config['namespace']}.data dummy
{convention_debug}"""
	if dependencies:
		content += f"""
# Check dependencies and wait for a player to connect (to get server version)
function {config['namespace']}:v{version}/load/check_dependencies
function {config['namespace']}:v{version}/load/valid_dependencies
"""
	else:
		content += f"""
# Confirm load
function {config['namespace']}:v{version}/load/confirm_load
"""
	write_versioned_function(config, "load/secondary", content)


	# Tick verification
	if is_in_write_queue(f"{config['build_datapack']}/data/{ns}/function/v{version}/tick.mcfunction"):
		write_file(f"{config['build_datapack']}/data/minecraft/tags/function/tick.json", stp.super_json_dump({"values": [f"{ns}:v{version}/load/tick_verification"]}))
		write_versioned_function(config, "load/tick_verification",
f"""
execute if score #{ns}.major load.status matches {major} if score #{ns}.minor load.status matches {minor} if score #{ns}.patch load.status matches {patch} run function {ns}:v{version}/tick

""")

	# Link smart_ore_generation library functions
	if OFFICIAL_LIBS["smart_ore_generation"]["is_used"]:
		for function_tag in ["denied_dimensions", "generate_ores", "post_generation"]:
			function_path: str = f"{config['build_datapack']}/data/{ns}/function/calls/smart_ore_generation/{function_tag}.mcfunction"
			if FILES_TO_WRITE.get(function_path):
				json_file: dict = {"values": [f"{ns}:calls/smart_ore_generation/{function_tag}"]}
				path: str = f"{config['build_datapack']}/data/smart_ore_generation/tags/function/v1/signals/{function_tag}.json"
				write_file(path, stp.super_json_dump(json_file))


	# For each used library, show message
	used_libs: str = ', '.join(data["name"] for data in OFFICIAL_LIBS.values() if data["is_used"])
	if used_libs:
		stp.info(f"Summary of the official supported libraries used in the datapack: {used_libs}")

	## Write check_dependencies and valid_dependencies functions now that we have all the dependencies
	encoder_checks = ""
	decoder_checks = ""
	for lib_ns, value in dependencies:

		# Encoder check
		encoder_command: str = f"scoreboard players set #dependency_error {ns}.data 1"
		encoder_checks += check_version(config, lib_ns, value, encoder_command)

		# Decoder check
		name, url = value["name"], value["url"]
		lib_version = ".".join(map(str, value["version"]))
		decoder_command: str = f'tellraw @a {{"text":"- [{name} (v{lib_version}+)]","color":"gold","click_event":{{"action":"open_url","url":"{url}"}}}}'
		decoder_checks += check_version(config, lib_ns, value, decoder_command)

	# Write check_dependencies.mcfunction
	if dependencies:
		write_versioned_function(config, "load/check_dependencies",
f"""
## Check if {config['project_name']} is loadable (dependencies)
scoreboard players set #dependency_error {ns}.data 0
{encoder_checks}
""")

	# Waiting for player
	if dependencies:
		write_versioned_function(config, "load/valid_dependencies",
f"""
# Waiting for a player to get the game version, but stop function if no player found
execute unless entity @p run schedule function {ns}:v{version}/load/valid_dependencies 1t replace
execute unless entity @p run return 0
execute store result score #game_version {ns}.data run data get entity @p DataVersion

# Check if the game version is supported
scoreboard players set #mcload_error {ns}.data 0
execute unless score #game_version {ns}.data matches {DATA_VERSION}.. run scoreboard players set #mcload_error {ns}.data 1

# Decode errors
execute if score #mcload_error {ns}.data matches 1 run tellraw @a {{"text":"{config['project_name']} Error: This version is made for Minecraft {MINECRAFT_VERSION}+.","color":"red"}}
execute if score #dependency_error {ns}.data matches 1 run tellraw @a {{"text":"{config['project_name']} Error: Libraries are missing\\nplease download the right {config['project_name']} datapack\\nor download each of these libraries one by one:","color":"red"}}
{decoder_checks}
# Load {config['project_name']}
execute if score #game_version {ns}.data matches 1.. if score #mcload_error {ns}.data matches 0 if score #dependency_error {ns}.data matches 0 run function {ns}:v{version}/load/confirm_load

""")

	return

