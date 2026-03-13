
# Imports
import stouputils as stp
from beet import Context, Language, TextFileBase

from ....core.utils.io import set_json_encoder
from .utils import handle_file, lang


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.auto.lang_file'")
def beet_default(ctx: Context, desc: str = "Generating lang file") -> None:
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
	args: list[TextFileBase[str]] = [
		content for content in files_to_process.values()
		if isinstance(content, TextFileBase)
	]
	for content in stp.colored_for_loop(args, desc=desc, color=stp.BLUE):
		handle_file(ctx, content)

	# Update the lang file
	lang.update(ctx.assets.languages.get("minecraft:en_us", Language()).data)
	ctx.assets.languages["minecraft:en_us"] = set_json_encoder(Language(dict(sorted(lang.items()))))
	pass

