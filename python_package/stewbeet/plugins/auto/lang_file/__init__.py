
# Imports
from beet import Advancement, Context, Function, ItemModifier, Language, LootTable
from stouputils.decorators import measure_time
from stouputils.io import super_json_dump
from stouputils.parallel import multithreading
from stouputils.print import BLUE, progress

from .utils import handle_file, lang


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.auto.lang_file'")
def beet_default(ctx: Context):
	""" Main entry point for the lang file plugin.
	This plugin handles language file generation for the datapack.

	Args:
		ctx (Context): The beet context.
	"""
	# Get all functions and loot tables
	files_to_process: dict[str, Function | LootTable] = {}
	files_to_process.update(ctx.data.functions)
	files_to_process.update(ctx.data.loot_tables)
	files_to_process.update(ctx.data.item_modifiers)
	files_to_process.update(ctx.data.advancements)

	# Process all files
	args: list[tuple[Context, str, Function | LootTable | ItemModifier, Advancement]] = [
		(ctx, file, content) for (file, content) in files_to_process.items()
		if True
	]
	multithreading(handle_file, args, use_starmap=True, desc="Generating lang file", max_workers=min(32, len(args)), color=BLUE)

	# Update the lang file
	lang.update(ctx.assets.languages.get("minecraft:en_us", Language()).data)
	ctx.assets.languages["minecraft:en_us"] = Language(super_json_dump(lang))
	pass

