
# Imports
import stouputils as stp
from beet import Context, PngFile

from ....core import Item, Mem
from ...initialize.source_lore_font import create_source_lore_font, find_pack_png


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.last_final'")
def beet_default(ctx: Context):
	if Mem.ctx is None: # pyright: ignore[reportUnnecessaryComparison]
		Mem.ctx = ctx

	# If source lore is present and there are item definitions using it, create the source lore font
	pack_icon_path: str = Mem.ctx.meta.get("stewbeet", {}).get("pack_icon_path", "")
	source_lore: str = Mem.ctx.meta.get("stewbeet", {}).get("source_lore", "")
	if pack_icon_path and source_lore:
		for item in Mem.definitions.keys():
			obj = Item.from_id(item)
			if source_lore in obj.components.get("lore", []):
				create_source_lore_font(pack_icon_path)
				break

	# Add the pack icon to the output directory for datapack and resource pack
	pack_icon = find_pack_png()
	if pack_icon:
		Mem.ctx.data.extra["pack.png"] = PngFile(source_path=pack_icon)
		all_assets = set(Mem.ctx.assets.all())
		if len(all_assets) > 0:
			Mem.ctx.assets.extra["pack.png"] = PngFile(source_path=pack_icon)

