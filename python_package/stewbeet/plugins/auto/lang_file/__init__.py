
# Imports
import stouputils as stp
from beet import Context, Language, TextFileBase

from .utils import handle_file, lang


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.auto.lang_file'")
def beet_default(ctx: Context):
	""" Main entry point for the lang file plugin.
	This plugin handles language file generation for the datapack.

	Args:
		ctx (Context): The beet context.
	"""
	# Get all functions and loot tables
	files_to_process: dict[str, TextFileBase[str] | None] = {}
	files_to_process.update(ctx.data.loot_tables)	# type: ignore # Idk why, but this is needed to ensure loot tables are processed
	files_to_process.update(dict(ctx.data.all()))	# type: ignore

	# Process all files
	args: list[tuple[Context, TextFileBase[str]]] = [
		(ctx, content) for content in files_to_process.values()
		if isinstance(content, TextFileBase)
	]
	stp.multithreading(handle_file, args, use_starmap=True, desc="Generating lang file", max_workers=min(32, len(args)), color=stp.BLUE)

	# Update the lang file
	lang.update(ctx.assets.languages.get("minecraft:en_us", Language()).data)
	ctx.assets.languages["minecraft:en_us"] = Language(stp.json_dump(dict(sorted(lang.items()))))
	pass

