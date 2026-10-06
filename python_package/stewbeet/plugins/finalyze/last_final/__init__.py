
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
	if (
		source_lore and uses_font(source_lore, f"{ctx.project_id}:{TOOLTIP_FONT}")
		and any(source_lore in Item.from_id(item).components.get("lore", []) for item in Mem.definitions)
	):
		create_source_lore_font(pack_icon_path)

	# Add the pack icon to the output directory for datapack and resource pack
	pack_icon = find_pack_png()
	if pack_icon:
		Mem.ctx.data.extra["pack.png"] = PngFile(source_path=pack_icon)
		all_assets = set(Mem.ctx.assets.all())
		if len(all_assets) > 0:
			Mem.ctx.assets.extra["pack.png"] = PngFile(source_path=pack_icon)

	# A macro line missing its leading $, or a $ line using no macro, does not run as written
	lines: list[tuple[str, int, str]] = [
		(func, i, line) for func, obj in Mem.ctx.data.functions.items() for i, line in enumerate(obj.text.splitlines())
	]
	for func, i, line in lines:
		if line.startswith("$") and "$(" not in line:
			stp.warning(
				f"Function '{func}' line {i+1} starts with '$' but does not contain a macro, "
				f"the function will not be able to execute: '{line}'"
			)
		elif "$(" in line and not line.startswith(("$","#")):
			stp.warning(
				f"Function '{func}' line {i+1} appears to use macros but does not start with '$', "
				f"execution will not be as expected: '{line}'"
			)

