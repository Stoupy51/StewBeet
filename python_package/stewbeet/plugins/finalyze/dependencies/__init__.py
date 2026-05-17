
# Imports
import stouputils as stp
from beet import Context
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.constants import LATEST_MC_VERSION, MORE_DATA_VERSIONS
from ....core.utils.io import write_function, write_tag, write_versioned_function
from ....dependencies.bookshelf import BOOKSHELF_MODULES
from ....dependencies.download_manager import get_lib_paths
from ....dependencies.official_libs import OFFICIAL_LIBS, official_lib_used


# Utility functions
def check_version(lib_ns: str, data: JsonDict, run_command: str) -> str:
	""" Check version compatibility for a dependency.

	Args:
		lib_ns (str): The namespace of the library to check
		data (dict): The dependency data containing version info
		run_command (str): The command to run if version check fails

	Returns:
		str: The version check commands
	"""
	ns: str = Mem.ctx.project_id
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


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.dependencies'")
def beet_default(ctx: Context) -> None:
	"""Main entry point for the dependencies plugin.
	This plugin handles dependency management, version checking, and load sequence setup.

	Args:
		ctx (Context): The beet context.
	"""
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# Get namespace and version
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	assert ctx.project_version, "Project version is not set. Please set it in the project configuration."
	assert ctx.project_name, "Project name is not set. Please set it in the project configuration."
	assert ctx.project_author, "Project author is not set. Please set it in the project configuration."
	ns: str = ctx.project_id
	version: str = ctx.project_version
	major, minor, patch = version.split(".")
	project_name: str = ctx.project_name
	author: str = ctx.project_author

	# Track newly found official libraries
	newly_found_libs: list[str] = []

	# Find if furnace_nbt_recipes, common_signals, realistic_explosion, itemio are used
	for lib in ["furnace_nbt_recipes", "common_signals", "realistic_explosion", "itemio", "smithed.actionbar", "player_motion"]:
		if ns != lib:
			for function in ctx.data.functions.values():
				if lib in function.text:
					if not official_lib_used(lib):
						newly_found_libs.append(lib)
					break

	# Find for each bookshelf module if it is used
	if ns != "bookshelf":
		for module_ns in BOOKSHELF_MODULES.keys():
			for function in ctx.data.functions.values():
				if f"#{module_ns}:" in function.text:
					if not official_lib_used(module_ns):
						newly_found_libs.append(module_ns)
					break

	# Debug message for newly found libraries
	if newly_found_libs:
		stp.debug(f"Found the use of official supported libraries: {', '.join(newly_found_libs)}, adding them to the datapack")

	# Download newly-found libs now that is_used flags are set
	get_lib_paths(ctx)

	# Get all dependencies (official and custom)
	dependencies: list[tuple[str, JsonDict]] = [(lib_ns, data) for lib_ns, data in OFFICIAL_LIBS.items() if data["is_used"] and not data.get("no_lantern_load", False)]
	load_dependencies: list[tuple[str, JsonDict]] = list(ctx.meta.get("stewbeet", {}).get("load_dependencies", {}).items())
	if load_dependencies:
		dependencies += [(k, v) for k, v in load_dependencies if not v.get("no_lantern_load", False)]
	# Setup Lantern Load
	write_tag("minecraft:load", ctx.data.function_tags, ["#load:_private/load"])
	write_tag("load:_private/init", ctx.data.function_tags, ["load:_private/init"])
	write_tag("load:_private/load", ctx.data.function_tags, [
		"#load:_private/init",
		{"id": "#load:pre_load", "required": False},
		{"id": "#load:load", "required": False},
		{"id": "#load:post_load", "required": False}
	])

	write_function("load:_private/init", """
# Reset scoreboards so packs can set values accurate for current load.
scoreboard objectives add load.status dummy
scoreboard players reset * load.status
""", overwrite=True)

	# Setup load json files
	write_tag("load:load", ctx.data.function_tags, [f"#{ns}:load"])
	values: list[str | JsonDict] = [f"#{ns}:enumerate", f"#{ns}:resolve"]
	if dependencies:
		write_tag(f"{ns}:enumerate", ctx.data.function_tags, [f"#{ns}:dependencies"], prepend=True)

	write_tag(f"{ns}:load", ctx.data.function_tags, values)

	if dependencies:
		calls: list[JsonDict] = [
			{"id": f"#{dep_ns}:load" if not dep_ns.startswith("bs.") else "#bs.load:load", "required": False}
			for dep_ns, _ in dependencies
		]
		# Remove duplicates while preserving order
		seen: set[str] = set()
		unique_calls: list[JsonDict] = []
		for call in calls:
			call_id = call["id"]
			if call_id not in seen:
				seen.add(call_id)
				unique_calls.append(call)

		write_tag(f"{ns}:dependencies", ctx.data.function_tags, unique_calls)

	# Write secondary function
	authors: list[str] = author.replace(",", " ").replace("  ", " ").split(" ")
	convention_debug: str = "".join([f"tag {author} add convention.debug\n" for author in authors])

	content: str = f"""
# {project_name}
scoreboard objectives add {ns}.data dummy
{convention_debug}"""

	if dependencies:
		content += f"""
# Check dependencies and wait for a player to connect (to get server version)
function {ns}:v{version}/load/check_dependencies
function {ns}:v{version}/load/valid_dependencies
"""
	else:
		content += f"""
# Confirm load
function {ns}:v{version}/load/confirm_load
"""

	write_versioned_function("load/secondary", content)

	# Tick verification
	tick_path: str = f"{ns}:v{version}/tick"
	if tick_path in ctx.data.functions:
		write_tag("minecraft:tick", ctx.data.function_tags, [f"{ns}:v{version}/load/tick_verification"])
		write_versioned_function("load/tick_verification", f"""
execute if score #{ns}.major load.status matches {major} if score #{ns}.minor load.status matches {minor} if score #{ns}.patch load.status matches {patch} run function {ns}:v{version}/tick
""")

	# Link smart_ore_generation library functions
	if OFFICIAL_LIBS["smart_ore_generation"]["is_used"]:
		for function_tag in ["denied_dimensions", "generate_ores", "post_generation"]:
			function_path: str = f"{ns}:calls/smart_ore_generation/{function_tag}"
			if function_path in ctx.data.functions:
				write_tag(f"smart_ore_generation:v1/signals/{function_tag}", ctx.data.function_tags, [function_path])

	# For each used library, show message
	used_libs: list[str] = [data["name"] for data in OFFICIAL_LIBS.values() if data["is_used"]]
	if used_libs:
		stp.info(f"Summary of the official supported libraries used in the datapack: {', '.join(used_libs)}")

	# Write check_dependencies and valid_dependencies functions now that we have all the dependencies
	if dependencies:
		encoder_checks: str = ""
		decoder_checks: str = ""

		for lib_ns, value in dependencies:
			if "version" not in value:
				stp.warning(f"Skipping version check for '{lib_ns}': version not resolved (download may have failed).")
				continue

			# Encoder check
			encoder_command: str = f"scoreboard players set #dependency_error {ns}.data 1"
			encoder_checks += check_version(lib_ns, value, encoder_command)

			# Decoder check
			name: str = value["name"]
			url: str = value["url"]
			lib_version: str = ".".join(map(str, value["version"]))
			decoder_command: str = f'tellraw @a {{"text":"- [{name} (v{lib_version}+)]","color":"gold","click_event":{{"action":"open_url","url":"{url}"}}}}'
			decoder_checks += check_version(lib_ns, value, decoder_command)

		# Write check_dependencies.mcfunction
		write_versioned_function("load/check_dependencies", f"""
## Check if {project_name} is loadable (dependencies)
scoreboard players set #dependency_error {ns}.data 0
{encoder_checks}
""")

		# Get Minecraft version (default to latest known if not set) and data version
		mc_version: str = ctx.minecraft_version or LATEST_MC_VERSION
		if ctx.meta.get("mc_supports"):
			mc_supports: list[str] = ctx.meta["mc_supports"]
			# Only keep valid versions (excluding 'w', 'b', 'pre' versions)
			mc_supports = [x for x in mc_supports if stp.version_to_float(x, error=False) is not None]
			minimum = min(mc_supports, key=stp.version_to_float)
			if stp.version_to_float(minimum) < stp.version_to_float(mc_version):
				mc_version = minimum
		mc_version_tuple: tuple[int, ...] = tuple(int(x) for x in mc_version.split(".") if x.isdigit())
		data_version: int = MORE_DATA_VERSIONS.get(mc_version_tuple, max(MORE_DATA_VERSIONS.values(), default=0))

		# Write valid_dependencies.mcfunction
		mc_error_msg: str = f'"{project_name} Error: This version is made for Minecraft {mc_version}+."'
		dep_error_msg: str = f'"{project_name} Error: Libraries are missing\\nplease download the right {project_name} datapack\\nor download each of these libraries one by one:"'

		write_versioned_function("load/valid_dependencies", f"""# Waiting for a player to get the game version, but stop function if no player found
execute unless entity @p run return run schedule function {ns}:v{version}/load/valid_dependencies 1t replace
execute store result score #game_version {ns}.data run data get entity @p DataVersion

# Check if the game version is supported
scoreboard players set #mcload_error {ns}.data 0
execute unless score #game_version {ns}.data matches {data_version}.. run scoreboard players set #mcload_error {ns}.data 1

# Decode errors
execute if score #mcload_error {ns}.data matches 1 run tellraw @a {{"text":{mc_error_msg},"color":"red"}}
execute if score #dependency_error {ns}.data matches 1 run tellraw @a {{"text":{dep_error_msg},"color":"red"}}
{decoder_checks}
# Load {project_name}
execute if score #game_version {ns}.data matches 1.. if score #mcload_error {ns}.data matches 0 if score #dependency_error {ns}.data matches 0 run function {ns}:v{version}/load/confirm_load
""")

