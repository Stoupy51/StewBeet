
# Imports
import stouputils as stp
from beet import Context, Language

from ....core.__memory__ import Mem
from ....core.utils.io import set_json_encoder
from ....core.utils.text_component import iter_data_text_files
from .utils import handle_file, lang


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.auto.lang_file'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the lang file plugin.
	This plugin handles language file generation for the datapack.

	Args:
		ctx (Context): The beet context.
	"""
	Mem.ctx = ctx

	# Process every text file of the datapack, loot tables included
	for content in iter_data_text_files(ctx):
		handle_file(content)

	# Update the lang file
	lang.update(ctx.assets.languages.get("minecraft:en_us", Language()).data)
	ctx.assets.languages["minecraft:en_us"] = set_json_encoder(Language(dict(sorted(lang.items()))))
	pass

