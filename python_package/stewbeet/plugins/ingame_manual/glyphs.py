"""Glyph code points reserved by the manual.

The allocator itself lives in :mod:`stewbeet.core.utils.fonts.allocator` and is shared with every
other font generator; this module only owns the manual's own reserved characters and sizes.

Every visual element of the manual (item icon, recipe template, page background, invisible spacer)
is a PNG mapped to a private-use unicode character inside a Minecraft bitmap font. The reserved
glyph code points below are **alignment-critical** and are kept byte-identical to the v1 plugin so
existing template PNGs keep rendering correctly.
"""

# pyright: reportUnusedImport=false
# ruff: noqa: F401
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from ...core.utils.fonts import GlyphAllocator, get_font

# Reserved (static) glyph characters: DO NOT change the code points, they are alignment-critical.
NONE_FONT: str =					get_font(0x0000)
MEDIUM_NONE_FONT: str =				get_font(0x0001)
SMALL_NONE_FONT: str =				get_font(0x0002)
VERY_SMALL_NONE_FONT: str =			get_font(0x0003)
MICRO_NONE_FONT: str =				get_font(0x0004)
WIKI_NONE_FONT: str =				get_font(0x0010)
WIKI_INFO_FONT: str =				get_font(0x0011)
WIKI_RESULT_OF_CRAFT_FONT: str =	get_font(0x0012)
WIKI_INGR_OF_CRAFT_FONT: str =		get_font(0x0013)
HOME_FONT: str =					get_font(0x0014)  # NEW in v2: dialog "go to first page" arrow
SHAPED_2X2_FONT: str =				get_font(0x0015)
SHAPED_3X3_FONT: str =				get_font(0x0016)
FURNACE_FONT: str =					get_font(0x0017)
STONECUTTING_FONT: str =			get_font(0x0018)
PULVERIZING_FONT: str =				get_font(0x0019)
MINING_FONT: str =					get_font(0x0020)
AWAKENED_3X3_FONT: str =			get_font(0x0021)
AWAKENED_3X4_FONT: str =			get_font(0x0022)
GROWING_SEED_FONT: str =			get_font(0x0023)  # NEW in v2 (free slot next to mining/awakened)
HOVER_SHAPED_2X2_FONT: str =		get_font(0x0025)
HOVER_SHAPED_3X3_FONT: str =		get_font(0x0026)
HOVER_FURNACE_FONT: str =			get_font(0x0027)
HOVER_STONECUTTING_FONT: str =		get_font(0x0028)
HOVER_PULVERIZING_FONT: str =		get_font(0x0029)
HOVER_MINING_FONT: str =			get_font(0x0030)
HOVER_AWAKENED_3X3_FONT: str =		get_font(0x0031)
HOVER_AWAKENED_3X4_FONT: str =		get_font(0x0032)
HOVER_GROWING_SEED_FONT: str =		get_font(0x0033)  # NEW in v2
WIKI_GROWING_SEED_FONT: str =		get_font(0x0034)  # NEW in v2: growing seed wiki button icon
INVISIBLE_ITEM_FONT: str =			get_font(0x0035)  # Invisible item to place
INVISIBLE_ITEM_WIDTH: str =			INVISIBLE_ITEM_FONT + MICRO_NONE_FONT
BOOK_FONT: str =					get_font(0x0036)
AWAKENED_FORGE_STRUCT_FONT: tuple[str, str] = (get_font(0x0037), get_font(0x0038))

HOVER_EQUIVALENTS: dict[str, str] = {
	SHAPED_2X2_FONT: HOVER_SHAPED_2X2_FONT,
	SHAPED_3X3_FONT: HOVER_SHAPED_3X3_FONT,
	FURNACE_FONT: HOVER_FURNACE_FONT,
	STONECUTTING_FONT: HOVER_STONECUTTING_FONT,
	PULVERIZING_FONT: HOVER_PULVERIZING_FONT,
	MINING_FONT: HOVER_MINING_FONT,
	GROWING_SEED_FONT: HOVER_GROWING_SEED_FONT,
	AWAKENED_3X3_FONT: HOVER_AWAKENED_3X3_FONT,
	AWAKENED_3X4_FONT: HOVER_AWAKENED_3X4_FONT,
}

# First dynamically-allocated code point (high-res item icons, wiki result icons, page glyphs...)
DEFAULT_NEXT_CRAFT_FONT: int = 0x8000

# Bitmap placement of the book background glyph (shared BOOK_FONT and per-page overrides)
BOOK_ASCENT: int = 25
BOOK_HEIGHT: int = 300

# Bitmap placement of the home button glyph (shared HOME_FONT and per-page overrides)
HOME_ASCENT: int = 8
HOME_HEIGHT: int = 20

# Misc constants
SQUARE_SIZE: int = 32
FONT_FILE: str = "manual"
BORDER_SIZE: int = 2
HEAVY_WORKBENCH_CATEGORY: str = "__private_heavy_workbench"
