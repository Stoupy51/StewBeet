
# pyright: reportUnusedImport=false
# ruff: noqa: F401
# Imports
import json
from pathlib import Path

import stouputils as stp
from beet import Texture
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ...core import Mem
from ...core.utils.fonts import iter_fonts, merge_font_providers, uses_font
from .project_images import find_pack_png, find_tooltip_png
from .source_lore_colors import recolor_image, resolve_source_lore_color

# Constants
ASSETS_FOLDER: str = f"{stp.get_root_path(__file__)}/assets"
TOOLTIP_FONT: str = "tooltip"			# Font generated in the project namespace: <project_id>:tooltip
ICON_CHAR: str = "ꀁ"					# Glyph showing the project logo (only provided when a pack.png was found)
SPACER_CHAR: str = "뀁"				# 2px spacer glyph coming from the font "space" provider
ATLAS_TEXTURE: str = "font/tooltip"		# Character atlas, relative to textures/
ICON_TEXTURE: str = "tooltip/tooltip"	# Logo glyph, relative to textures/


# Utility functions
def is_icon_placeholder(component: TextComponent) -> bool:
	""" Whether a text component is the ``{"text": "ICON"}`` placeholder standing for the logo glyph.

	>>> is_icon_placeholder({"text": "ICON"}), is_icon_placeholder({"text": "nope"}), is_icon_placeholder("ICON")
	(True, False, False)
	"""
	return isinstance(component, dict) and component.get("text", "") == "ICON"


def warn_foreign_tooltip_font(source_lore: TextComponent) -> None:
	""" Warn when the source lore asks for a tooltip font belonging to another namespace.

	StewBeet only ever generates ``<project_id>:tooltip``, and only when something actually asks for
	it. A source lore naming ``someone_else:tooltip`` therefore gets no font at all and silently
	falls back to the default one in game. The templates ship ``_your_namespace:tooltip``, so this
	is what a project that renamed its id and not its source lore runs into.

	Args:
		source_lore	(TextComponent):	Source lore to inspect.
	"""
	expected: str = f"{Mem.ctx.project_id}:{TOOLTIP_FONT}"
	foreign: set[str] = {
		font for font in iter_fonts(source_lore)
		if font.endswith(f":{TOOLTIP_FONT}") and font != expected
	}
	for font in sorted(foreign):
		stp.warning(
			f"source_lore asks for the font '{font}', but this project only generates '{expected}'. "
			f"That font will never be created and the text using it falls back to the default one. "
			f"Rename it to '{expected}'."
		)


# Main functions to create the source lore font
def prepare_source_lore_font(source_lore: list[TextComponent]) -> str:
	""" Replace every ``ICON`` placeholder of the source lore with the logo glyph of the tooltip font.

	Args:
		source_lore	(list[TextComponent]):	Source lore to patch in place.
	Returns:
		str: Path to the ``pack.png`` backing the glyph, or "" when there is no placeholder or no logo.
	"""
	if not any(is_icon_placeholder(component) for component in source_lore):
		return ""

	# Without a logo, drop the placeholders so the lore never shows a literal "ICON"
	pack_icon: str | None = find_pack_png()
	if not pack_icon:
		source_lore[:] = [component for component in source_lore if not is_icon_placeholder(component)]
	else:
		glyph: JsonDict = {"text": ICON_CHAR, "color": "white", "italic": False, "font": f"{Mem.ctx.project_id}:{TOOLTIP_FONT}"}
		source_lore[:] = ["", *(glyph if is_icon_placeholder(component) else component for component in source_lore)]

	Mem.ctx.meta.setdefault("stewbeet", {})["source_lore"] = source_lore
	return pack_icon or ""


def create_source_lore_font(pack_icon: str = "") -> None:
	""" Create the ``<project_id>:tooltip`` font used by the source lore.

	The character atlas comes from a project-supplied ``tooltip.png`` when there is one (used as-is),
	otherwise from the packaged one, recolored according to ``source_lore_color``.

	Args:
		pack_icon	(str):	Path to the project ``pack.png``. When empty, the logo glyph provider is
			skipped so the font never points at a missing texture.
	"""
	namespace: str = Mem.ctx.project_id
	assets = Mem.ctx.assets[namespace]

	# Load the packaged font template, retargeting its "ns:" references to the project namespace
	template: str = Path(f"{ASSETS_FOLDER}/tooltip.json").read_text(encoding="utf-8").replace('"ns:', f'"{namespace}:')
	providers: list[JsonDict] = json.loads(template)["providers"]
	if not pack_icon:  # Drop the logo provider when there is no pack.png to feed it
		providers = [provider for provider in providers if provider.get("file") != f"{namespace}:{ICON_TEXTURE}.png"]

	# Merge the providers into the font, keeping the ones that were already there
	merge_font_providers(namespace, TOOLTIP_FONT, providers)

	# Character atlas: a project-supplied tooltip.png wins as-is, else recolor the packaged one
	override: str | None = find_tooltip_png()
	if override:
		assets.textures[ATLAS_TEXTURE] = Texture(source_path=override)
	else:
		atlas: Image.Image = Image.open(f"{ASSETS_FOLDER}/tooltip.png").convert("RGBA")
		target: tuple[int, int, int] | None = resolve_source_lore_color(pack_icon or None)
		assets.textures[ATLAS_TEXTURE] = Texture(recolor_image(atlas, target) if target else atlas)

	# Logo glyph texture
	if pack_icon:
		logo: Image.Image = Image.open(pack_icon).convert("RGBA")
		assets.textures[ICON_TEXTURE] = Texture(logo.resize((256, 256)) if logo.width > 256 else logo)


def delete_source_lore_font() -> None:
	""" Delete the source lore font and its textures if they exist. """
	assets = Mem.ctx.assets[Mem.ctx.project_id]
	if assets.fonts.get(TOOLTIP_FONT):
		del assets.fonts[TOOLTIP_FONT]
	for texture in (ATLAS_TEXTURE, ICON_TEXTURE):
		if assets.textures.get(texture):
			del assets.textures[texture]

