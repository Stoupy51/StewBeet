""" ``source_lore_color`` resolution.

The color analysis itself lives in :mod:`stewbeet.core.utils.fonts.colors`; this module only reads
the configuration and hands it over. The analysis helpers are re-exported because they are part of
this module's documented surface.
"""
# pyright: reportUnusedImport=false
# ruff: noqa: F401
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from ...core import Mem
from ...core.utils.fonts import (
	HUE_BUCKETS,
	MIN_SATURATION,
	MIN_VALUE,
	NO_RECOLOR_VALUES,
	Pixel,
	get_dominant_color,
	get_pixels,
	parse_color,
	recolor_image,
)


# Utility functions
def resolve_source_lore_color(logo_path: str | None = None) -> tuple[int, int, int] | None:
	""" Resolve the ``source_lore_color`` configuration into the color the atlas should use.

	Accepted values are ``"auto"`` (derive it from the logo), any color Pillow understands
	(``"#55FFFF"``, ``"gold"``, ``[85, 255, 255]``), or a falsy value / ``"none"`` to keep the packaged
	atlas colors untouched.

	Args:
		logo_path	(str | None):	Path to the logo used by the ``"auto"`` mode.
	Returns:
		tuple[int, int, int] | None: Target color, or None when no recolor should happen.
	"""
	raw: object = Mem.ctx.meta.get("stewbeet", {}).get("source_lore_color", "auto")
	return parse_color(raw, logo_path, config_key="source_lore_color")

