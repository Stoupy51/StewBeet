
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.constants import LATEST_MC_VERSION, MORE_DATA_VERSIONS
from ....core.utils.io import write_function, write_tag, write_versioned_function
from ....dependencies.download_manager import get_lib_paths
from ....dependencies.official_libs import OFFICIAL_LIBS, detection_markers, official_lib_used


# Utility functions
def check_version(lib_ns: str, data: JsonDict, run_command: str) -> str:
	""" Check version compatibility for a dependency.

	Args:
		lib_ns:      The namespace of the library to check
		data:        The dependency data containing version info
		run_command: The command to run if version check fails

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
	error_check: str = f"execute if score #dependency_error {ns}.data matches {is_decoder}"
	checks += f"{error_check} unless {score_major}.. run {run_command}\n"
	checks += f"{error_check} if {score_major} unless {score_minor}.. run {run_command}\n"
	if score_patch:
		checks += f"{error_check} if {score_major} if {score_minor} unless {score_patch}.. run {run_command}\n"
	return checks


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.dependencies'")
def beet_default(ctx: Context) -> None:
	"""Main entry point for the dependencies plugin.
	This plugin handles dependency management, version checking, and load sequence setup.

	Args:
		ctx: The beet context.
	"""
	Mem.ctx = ctx
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	assert ctx.project_version, "Project version is not set. Please set it in the project configuration."
	assert ctx.project_name, "Project name is not set. Please set it in the project configuration."
	assert ctx.project_author, "Project author is not set. Please set it in the project configuration."
	ns: str = ctx.project_id
	detect_libraries(ns)

	# Download newly-found libs now that is_used flags are set
	get_lib_paths(ctx)

	# Official libraries in use and custom ones, unless excluded from Lantern Load
	dependencies: list[tuple[str, JsonDict]] = [
		(lib_ns, data) for lib_ns, data in OFFICIAL_LIBS.items() if data["is_used"] and not data.get("no_lantern_load", False)
	]
	load_dependencies: list[tuple[str, JsonDict]] = list(ctx.meta.get("stewbeet", {}).get("load_dependencies", {}).items())
	dependencies += [(k, v) for k, v in load_dependencies if not v.get("no_lantern_load", False)]

	write_lantern_load(ns, dependencies)
	write_secondary(ns, has_dependencies=bool(dependencies))
	link_libraries(ns)
	if dependencies:
		write_dependency_checks(ns, dependencies)


def detect_libraries(ns: str) -> None:
	""" Mark as used every official library whose marker a function of the pack holds, reported in marker declaration order. """
	markers: dict[str, str] = detection_markers(ns)
	remaining: dict[str, str] = dict(markers)
	found_libs: set[str] = set()
	for function in Mem.ctx.data.functions.values():
		if not remaining:
			break
		text: str = function.text
		for marker in [m for m in remaining if m in text]:
			found_libs.add(remaining.pop(marker))

	# Declaration order keeps the debug message stable across builds
	newly_found_libs: list[str] = [lib_ns for lib_ns in markers.values() if lib_ns in found_libs and not official_lib_used(lib_ns)]
	if newly_found_libs:
		stp.debug(f"Found the use of official supported libraries: {', '.join(newly_found_libs)}, adding them to the datapack")


def write_lantern_load(ns: str, dependencies: list[tuple[str, JsonDict]]) -> None:
	""" Set Lantern Load up, the pack's load tag enumerating its dependencies' load tags first. """
	function_tags = Mem.ctx.data.function_tags
	write_tag("minecraft:load", function_tags, ["#load:_private/load"])
	write_tag("load:_private/init", function_tags, ["load:_private/init"])
	write_tag("load:_private/load", function_tags, [
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

	write_tag("load:load", function_tags, [f"#{ns}:load"])
	if dependencies:
		write_tag(f"{ns}:enumerate", function_tags, [f"#{ns}:dependencies"], prepend=True)
	write_tag(f"{ns}:load", function_tags, [f"#{ns}:enumerate", f"#{ns}:resolve"])
	if dependencies:
		# Bookshelf modules all load through one tag
		load_tags: list[str] = [f"#{dep_ns}:load" if not dep_ns.startswith("bs.") else "#bs.load:load" for dep_ns, _ in dependencies]
		write_tag(f"{ns}:dependencies", function_tags, [{"id": tag, "required": False} for tag in dict.fromkeys(load_tags)])


def write_secondary(ns: str, has_dependencies: bool) -> None:
	""" Write the secondary load function: the pack's score, the debug tag of its authors, then the dependency checks or the load. """
	version: str = Mem.ctx.project_version
	authors: list[str] = Mem.ctx.project_author.replace(",", " ").replace("  ", " ").split(" ")
	convention_debug: str = "".join([f"tag {author} add convention.debug\n" for author in authors])
	content: str = f"""
# {Mem.ctx.project_name}
scoreboard objectives add {ns}.data dummy
{convention_debug}"""
	if has_dependencies:
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


def link_libraries(ns: str) -> None:
	""" Run the tick function only once loaded, link the smart_ore_generation signals, and list the libraries in use. """
	ctx = Mem.ctx
	version: str = ctx.project_version
	major, minor, patch = version.split(".")
	if f"{ns}:v{version}/tick" in ctx.data.functions:
		write_tag("minecraft:tick", ctx.data.function_tags, [f"{ns}:v{version}/load/tick_verification"])
		write_versioned_function("load/tick_verification", f"""
execute if score #{ns}.major load.status matches {major} if score #{ns}.minor load.status matches {minor} if score #{ns}.patch load.status matches {patch} run function {ns}:v{version}/tick
""")  # noqa: E501

	if OFFICIAL_LIBS["smart_ore_generation"]["is_used"]:
		for function_tag in ["denied_dimensions", "generate_ores", "post_generation"]:
			function_path: str = f"{ns}:calls/smart_ore_generation/{function_tag}"
			if function_path in ctx.data.functions:
				write_tag(f"smart_ore_generation:v1/signals/{function_tag}", ctx.data.function_tags, [function_path])

	used_libs: list[str] = [data["name"] for data in OFFICIAL_LIBS.values() if data["is_used"]]
	if used_libs:
		stp.info(f"Summary of the official supported libraries used in the datapack: {', '.join(used_libs)}")


def write_dependency_checks(ns: str, dependencies: list[tuple[str, JsonDict]]) -> None:
	""" Write the functions checking each dependency's version, then the game version once a player gives it, before loading. """
	ctx = Mem.ctx
	version: str = ctx.project_version
	project_name: str = ctx.project_name
	encoder_checks: str = ""
	decoder_checks: str = ""
	for lib_ns, value in dependencies:
		if "version" not in value:
			stp.warning(f"Skipping version check for '{lib_ns}': version not resolved (download may have failed).")
			continue
		encoder_checks += check_version(lib_ns, value, f"scoreboard players set #dependency_error {ns}.data 1")
		lib_version: str = ".".join(map(str, value["version"]))
		decoder_command: str = (
			f'tellraw @a {{"text":"- [{value["name"]} (v{lib_version}+)]","color":"gold",'
			f'"click_event":{{"action":"open_url","url":"{value["url"]}"}}}}'
		)
		decoder_checks += check_version(lib_ns, value, decoder_command)

	write_versioned_function("load/check_dependencies", f"""
## Check if {project_name} is loadable (dependencies)
scoreboard players set #dependency_error {ns}.data 0
{encoder_checks}
""")

	mc_version: str = minimum_minecraft_version()
	mc_version_tuple: tuple[int, ...] = tuple(int(x) for x in mc_version.split(".") if x.isdigit())
	data_version: int = MORE_DATA_VERSIONS.get(mc_version_tuple, max(MORE_DATA_VERSIONS.values(), default=0))
	mc_error_msg: str = f'"{project_name} Error: This version is made for Minecraft {mc_version}+."'
	dep_error_msg: str = (
		f'"{project_name} Error: Libraries are missing\\nplease download the right {project_name} datapack\\n'
		'or download each of these libraries one by one:"'
	)
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
""")  # noqa: E501


def minimum_minecraft_version() -> str:
	""" The oldest Minecraft version the pack supports, the lowest release of `mc_supports` when below the project's version.

	The latest known version when the project sets none.
	"""
	mc_version: str = Mem.ctx.minecraft_version or LATEST_MC_VERSION
	if not Mem.ctx.meta.get("mc_supports"):
		return mc_version
	# Releases only, without 'w', 'b' or 'pre' versions
	mc_supports: list[str] = [
		x for x in Mem.ctx.meta["mc_supports"] if x != "infinite" and stp.version_to_float(x, error=False) is not None
	]
	minimum: str = min(mc_supports, key=stp.version_to_float)
	return minimum if stp.version_to_float(minimum) < stp.version_to_float(mc_version) else mc_version

