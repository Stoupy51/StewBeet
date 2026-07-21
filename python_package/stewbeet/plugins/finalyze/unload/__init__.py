
# Imports
from collections.abc import Callable
from dataclasses import dataclass, field
from re import Match, Pattern, compile
from typing import Literal
from zipfile import ZipFile

import stouputils as stp
from beet import Context

from ....core.__memory__ import Mem
from ....core.utils.io import write_unload_file, write_versioned_function
from ....dependencies.download_manager import DownloadedLib, get_lib_paths

# Constants
type UnloadFunctionKeys = Literal["items", "scoreboard_objectives", "storages", "blocks", "libraries", "entities_uuids", "entities_tags"]

# Regex patterns for scanning datapack functions
SCOREBOARD_OBJECTIVE_RE: Pattern[str] = compile(r"scoreboard objectives add ([^ ]+)")
ENTITY_UUID_RE: Pattern[str] = compile(
	r"summon [^ ]+"                              # entity type
	r"\s+(?:[\d~.-]+\s+){3}"                     # coordinates (x y z)
	r"\{.*UUID:\s*"                              # NBT UUID key
	r"(\[\s*I\s*;(?:\s*[\d.-]+\s*,){3}\s*[\d.-]+\s*\])"  # capture: [I; a, b, c, d]
)
ENTITY_TAGS_RE: Pattern[str] = compile(
	r"summon [^ ]+"                              # entity type
	r"\s+(?:[\d~.-]+\s+){3}"                     # coordinates (x y z)
	r"\{.*Tags:\s*"                              # NBT Tags key
	r'(\[(?:\s*["\'][0-9A-Za-z_.+-]+["\']\s*,?)+\s*\])'  # capture: ["tag", ...]
)

# Library unload function name constants
LIB_VALID_FILENAMES: set[str] = {"unload", "uninstall"}
LIB_SUFFIX_VARIANTS: set[str] = {"with_libraries", "with_libs", "libraries", "libs", "with-libraries", "with-libs"}
LIB_UNLOAD_FUNCTIONS: set[str] = {
	f"{base}_{suffix}" if sep == "_" else f"{base}-{suffix}" if sep == "-" else f"{base}{suffix}"
	for base in LIB_VALID_FILENAMES
	for suffix in LIB_SUFFIX_VARIANTS
	for sep in ("_", "-", "")
} | LIB_VALID_FILENAMES



# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.unload'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the unload plugin.
	This plugin sets up basic unload functions to clear entities, blocks, items,
	scoreboard objectives, and storages that are detected in the datapack functions.

	It also scans library ZIPs for custom unload functions and adds calls to them in the main unload function.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	ns: str = ctx.project_id
	version: str = ctx.project_version

	UnloadFunction(ctx, ns, version)

def uuid2inline(uuid: str) -> str:
	""" Convert a Minecraft NBT UUID list to inline UUID string format.

	Input:  '[I; -1234, 5678, -91011, 12131415]'  (four signed 32-bit ints)
	Output: 'fffffb2e-0000162e-fffed97d-00b8e8f7'  (eight hex chars per int, joined with dashes)
	"""
	# Parse the four signed 32-bit integers from "[I; a, b, c, d]"
	content: str = uuid[uuid.index(";") + 1 : uuid.rindex("]")]
	ints: list[int] = [int(part.strip()) for part in content.split(",")]

	# Convert each signed int to 8 hex digits (two's complement -> unsigned 32-bit)
	hex_str: str = "".join(f"{(n + (1 << 32)) % (1 << 32):08x}" for n in ints)

	# Format as the standard UUID layout: 8-4-4-4-12
	return f"{hex_str[:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:]}"

@dataclass(slots=True)
class UnloadEntry:
	""" One category of commands to generate during unload. """
	header: str
	commands: set[str] = field(default_factory=set[str])
	callback: Callable[[set[str]], None] | None = None


class UnloadFunction:
	""" Class to generate the unload functions for the datapack """
	def __init__(self, ctx: Context, ns: str, version: str) -> None:
		self.ctx = ctx
		self.ns = ns
		self.version = version
		self.entries: dict[UnloadFunctionKeys, UnloadEntry] = self.build_entries()
		self.scan_datapack()
		for lib in get_lib_paths(self.ctx):
			self.unload_library(lib)
		self.write_unload_function()

	# -- Callbacks (written at most once per build, use overwrite=True) ------
	def write_safe_kill(self, _commands: set[str]) -> None:
		write_versioned_function("unload/safe_kill", """
# This function is used to safely kill entities by teleporting them to the void before killing them to prevent item drops
tp @s ~ -10000 ~
kill @s
""", overwrite=True)

	def write_destroy_block(self, _commands: set[str]) -> None:
		write_versioned_function("unload/destroy_block", """
# This function is called by the main unload function to destroy custom blocks
setblock ~ ~ ~ air
kill @s
""", overwrite=True)

	def write_unload_with_libraries(self, commands: set[str]) -> None:
		write_versioned_function("unload_with_libraries", f"""
#> unload_with_libraries
# This function is called by the user if they want to unload the pack and all it's libraries
# Be careful this can lead to issues if a library is used by another pack and had some data stored

# Unload the pack itself
function {self.ns}:v{self.version}/unload

# Unload libraries
{"\n".join(sorted(commands))}
""", overwrite=True, tags=[f"{self.ns}:unload_with_libraries"])

	# -- Setup ---------------------------------------------------------------
	def build_entries(self) -> dict[UnloadFunctionKeys, UnloadEntry]:
		ns = self.ns
		version = self.version
		return {
			"items": UnloadEntry(
				header="# Clear custom items",
				commands={f'clear @a *[custom_data~{{"{ns}":{{}}}}]'} if Mem.definitions else set(),
			),
			"blocks": UnloadEntry(
				header="# Destroy custom blocks",
				commands={
					f"execute as @e[type=minecraft:item_display,tag={ns}.custom_block] at @s run function {ns}:v{version}/unload/destroy_block",
				} if self.ctx.data.function_tags.get("smithed.custom_block:event/on_place") else set(),
				callback=self.write_destroy_block,
			),
			"entities_uuids": UnloadEntry(
				header="# Kill entities spawned with a custom UUID",
				callback=self.write_safe_kill,
			),
			"entities_tags": UnloadEntry(
				header="# Kill entities with custom tags",
				callback=self.write_safe_kill,
			),
			"scoreboard_objectives": UnloadEntry(header="# Remove scoreboard objectives"),
			"storages": UnloadEntry(header="# Clear storages"),
			"libraries": UnloadEntry(header="", callback=self.write_unload_with_libraries),
		}

	# -- Scanning ------------------------------------------------------------
	def scan_datapack(self) -> None:
		ns = self.ns
		# Each entry: (pattern, callback) where callback returns the unload commands for a match
		regexes: dict[UnloadFunctionKeys, tuple[Pattern[str], Callable[[Match[str]], set[str]]]] = {
			# scoreboard objectives add <name>  ->  scoreboard objectives remove <name>
			"scoreboard_objectives": (
				SCOREBOARD_OBJECTIVE_RE,
				lambda match: {f"scoreboard objectives remove {match.group(1)}"},
			),
			# data modify storage <ns:key> <field>  ->  data remove storage <ns:key> <field>
			"storages": (
				compile(rf"data modify storage ({ns}:\w+) (\w+)"),
				lambda match: {f"data remove storage {match.group(1)} {match.group(2)}"},
			),
			# summon ... {UUID:[I; a, b, c, d]}  ->  execute as <inline-uuid> ... run function .../unload/safe_kill
			"entities_uuids": (
				ENTITY_UUID_RE,
				lambda match: {f"execute as {uuid2inline(match.group(1))} at @s run function {ns}:v{self.version}/unload/safe_kill"},
			),
			# summon ... {Tags:["tag1", "tag2"]}  ->  execute as @e[tag=<ns_tag>] ... run function .../unload/safe_kill
			"entities_tags": (
				ENTITY_TAGS_RE,
				lambda match: {
					f"execute as @e[tag={tag}] at @s run function {ns}:v{self.version}/unload/safe_kill"
					for tag in (t.strip(' "\'') for t in match.group(1)[1:-1].split(","))
					if tag.startswith(ns)
				},
			),
		}

		for func in self.ctx.data.functions.values():
			for line in func.text.splitlines():
				# Skip macro lines (start with '$') — their arguments are dynamic and can't be statically unloaded
				if line.lstrip().startswith("$"):
					continue
				for key, (regex, callback) in regexes.items():
					match = regex.search(line)
					if match:
						self.entries[key].commands.update(callback(match))

	def unload_library(self, lib: DownloadedLib) -> None:
		""" Scan a library ZIP for unload functions and add them to the libraries entry.

		Precision order:
		1. v{version}/{filename}.mcfunction
		2. {filename}.mcfunction
		3. #{filename}.json

		Valid filenames: unload, uninstall (and variants with -/_ and with-libraries/with-libs/libraries/libs suffix)
		"""
		if lib.datapack_path is None:
			stp.warning(f"Library '{lib.lib_ns}' does not have a datapack path, skipping unload function scan.")
			return
		version: str = ".".join(str(x) for x in lib.version)
		data_folder: str = f"data/{lib.lib_ns}/"

		search_path: dict[str, str] = {
			"tags/function/%s.json": f"function #{lib.lib_ns}:%s",
			"function/%s.mcfunction": f"function {lib.lib_ns}:%s",
			f"function/v{version}/%s.mcfunction": f"function {lib.lib_ns}:v{version}/%s",
		}
		valid_files: list[tuple[str, str]] = [
			(path % filename, call % filename)
			for path, call in search_path.items()
			for filename in LIB_UNLOAD_FUNCTIONS
		]

		with ZipFile(lib.datapack_path) as zip_file:
			files_in_lib: set[str] = {
				entry[len(data_folder):]
				for entry in zip_file.namelist()
				if entry.startswith(data_folder)
			}
			for path, function_call in valid_files:
				if path in files_in_lib:
					self.entries["libraries"].commands.add(function_call)
					return

	# -- Writing -------------------------------------------------------------
	def write_unload_function(self) -> None:
		if all(len(entry.commands) == 0 for entry in self.entries.values()):
			return
		content: str = "\n\n".join(
			f"{entry.header}\n{'\n'.join(sorted(entry.commands))}"
			for entry in self.entries.values()
			if entry.commands and entry.header
		)
		for entry in self.entries.values():
			if entry.commands and entry.callback is not None:
				entry.callback(entry.commands)
		write_unload_file(content)

