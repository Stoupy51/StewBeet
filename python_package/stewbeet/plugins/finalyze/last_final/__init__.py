
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import stouputils as stp
from beet import Context, PngFile

from ....core import Item, Mem
from ...initialize.project_images import find_pack_png
from ...initialize.source_lore_font import TOOLTIP_FONT, create_source_lore_font, uses_font


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.last_final'")
def beet_default(ctx: Context):
	Mem.ctx = ctx

	# If the source lore uses the tooltip font and there are item definitions using it, create the font
	pack_icon_path: str = Mem.ctx.meta.get("stewbeet", {}).get("pack_icon_path", "")
	source_lore: str = Mem.ctx.meta.get("stewbeet", {}).get("source_lore", "")
	if source_lore and uses_font(source_lore, f"{ctx.project_id}:{TOOLTIP_FONT}"):
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

	# Warn user if there are functions using macros that are missing $ in the first line,
	# which would cause them to not be executed as expected (and the other way: $ but no macros used)
	for func, obj in Mem.ctx.data.functions.items():
		for i, line in enumerate(obj.text.splitlines()):
			if line.startswith("$") and "$(" not in line:
				stp.warning(f"Function '{func}' line {i+1} starts with '$' but does not contain a macro, the function will not be able to execute: '{line}'")
			elif "$(" in line and not line.startswith(("$","#")):
				stp.warning(f"Function '{func}' line {i+1} appears to use macros but does not start with '$', execution will not be as expected: '{line}'")

