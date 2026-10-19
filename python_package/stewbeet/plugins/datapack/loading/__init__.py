""" ⏳ Sets up the load functions of the datapack, completed by `stewbeet.plugins.finalyze.dependencies`. """
# ruff: noqa: E501
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, ContextIntProvider
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.item import Item
from ....core.utils.io import write_load_file, write_predicate, write_tag, write_versioned_function
from ...finalyze.dependencies import minimum_minecraft_version


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.datapack.loading'")
def beet_default(ctx: Context):
	""" Main entry point for the datapack loading plugin.

	Requires plugin `stewbeet.plugins.finalyze.dependencies` later in the pipeline to complete.

	Args:
		ctx: The beet context.
	"""
	# Assertions
	Mem.ctx = ctx
	assert ctx.project_version, "Project version is not set. Please set it in the project configuration."
	assert ctx.project_id, "Project ID is not set. Please set it in the project configuration."
	assert ctx.project_version.count(".") == 2, "Project version must be in the format 'major.minor.patch'."

	# Get basic project information
	major, minor, patch = ctx.project_version.split(".")

	# Setup enumerate and resolve functions
	write_versioned_function("load/enumerate",
f"""
# If current major is too low, set it to the current major
execute unless score #{ctx.project_id}.major load.status matches {major}.. run scoreboard players set #{ctx.project_id}.major load.status {major}

# If current minor is too low, set it to the current minor (only if major is correct)
execute if score #{ctx.project_id}.major load.status matches {major} unless score #{ctx.project_id}.minor load.status matches {minor}.. run scoreboard players set #{ctx.project_id}.minor load.status {minor}

# If current patch is too low, set it to the current patch (only if major and minor are correct)
execute if score #{ctx.project_id}.major load.status matches {major} if score #{ctx.project_id}.minor load.status matches {minor} unless score #{ctx.project_id}.patch load.status matches {patch}.. run scoreboard players set #{ctx.project_id}.patch load.status {patch}
""")

	write_versioned_function("load/resolve",
f"""
# If correct version, load the datapack
execute if score #{ctx.project_id}.major load.status matches {major} if score #{ctx.project_id}.minor load.status matches {minor} if score #{ctx.project_id}.patch load.status matches {patch} run function {ctx.project_id}:v{ctx.project_version}/load/main
""")

	# Setup enumerate and resolve function tags
	write_tag(f"{ctx.project_id}:enumerate", ctx.data.function_tags, [f"{ctx.project_id}:v{ctx.project_version}/load/enumerate"])
	write_tag(f"{ctx.project_id}:resolve", ctx.data.function_tags, [f"{ctx.project_id}:v{ctx.project_version}/load/resolve"])

	write_enabled_tag(ctx)

	# Setup load main function
	write_versioned_function("load/main",
f"""
# Avoiding multiple executions of the same load function
execute unless score #{ctx.project_id}.loaded load.status matches 1 run function {ctx.project_id}:v{ctx.project_version}/load/secondary
""")

	# Confirm load, with the storage representation of every item in the definitions
	items_storage: str = ""
	if Mem.definitions and ctx.meta.get("stewbeet", {}).get("items_storage", True):
		items_storage = f"\n# Items storage\ndata modify storage {ctx.project_id}:items all set value {{}}\n" + "".join(
			f"data modify storage {ctx.project_id}:items all.{item} set value " + stp.json_dump(storage_data(Item.from_id(item)), max_level = 0)
			for item in Mem.definitions
		)

	# Write the loading tellraw and score, along with the final dataset
	project_name = ctx.project_name or ctx.project_id
	write_load_file(f"""
# Confirm load
tellraw @a[tag=convention.debug] {{"text":"[Loaded {project_name} v{ctx.project_version}]","color":"green"}}
scoreboard players set #{ctx.project_id}.loaded load.status 1
""" + (f"function {ctx.project_id}:v{ctx.project_version}/load/set_items_storage\n" if items_storage else ""))

	# Write the items storage function separately to avoid having a huge load function
	if items_storage:
		write_versioned_function("load/set_items_storage", items_storage)


def write_enabled_tag(ctx: Context) -> None:
	""" The Smithed "pack enabled tag" convention: a predicate tag and version providers other packs read, whatever the load order.

	Minecraft 26.2 and older refuse the predicate's `type` key, so a pack supporting any of them does not get it.
	"""
	if stp.version_to_float(minimum_minecraft_version()) < stp.version_to_float("26.3"):
		return
	ns, version = ctx.project_id, ctx.project_version
	write_predicate(f"{ns}:v{version}/installed", {"type": "minecraft:random_chance", "chance": 1})
	write_tag(f"{ns}:installed", ctx.data.predicate_tags, [f"{ns}:v{version}/installed"])
	for part, number in zip(("major", "minor", "patch"), version.split("."), strict=True):
		ctx.data.context_int_providers[f"{ns}:v{version}/{part}"] = ContextIntProvider(number)
		write_tag(f"{ns}:{part}", ctx.data.context_int_provider_tags, [f"{ns}:v{version}/{part}"])


def storage_data(obj: Item) -> JsonDict:
	""" An item as the items storage holds it, every component namespaced and its item model first when it has one. """
	components: JsonDict = {"minecraft:item_model": ""}
	for k, v in obj.components.items():
		components[k if ":" in k else f"!minecraft:{k[1:]}" if k.startswith("!") else f"minecraft:{k}"] = v
	if components["minecraft:item_model"] == "":
		del components["minecraft:item_model"]
	return {"id": obj.base_item, "count": 1, "components": components}

