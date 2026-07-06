"""Glyph (bitmap-font) allocation for the manual.

This module replaces the old class-level globals in ``ingame_manual.shared_import``
(``SharedMemory.next_craft_font`` / ``SharedMemory.font_providers``) with a proper,
instance-owned :class:`GlyphAllocator`.

Every visual element of the manual (item icon, recipe template, page background,
invisible spacer) is a PNG mapped to a private-use unicode character inside a Minecraft
bitmap font. The reserved glyph code points below are **alignment-critical** and are kept
byte-identical to the v1 plugin so existing template PNGs keep rendering correctly.
"""

# Imports
import threading
from dataclasses import dataclass, field

import stouputils as stp
from stouputils.typing import JsonDict


# Font code-point helpers (kept identical to v1 for pixel alignment)
def get_font(i: int) -> str:
	""" Return the unicode character used for a glyph index.

	Minecraft only allows characters starting at 0x0020, so the index is offset by that.

	>>> get_font(0)
	' '
	>>> get_font(0x0035) == chr(0x0055)
	True
	"""
	i += 0x0020  # Minecraft only allows starting at this value
	if i > 0xffff:
		stp.error(f"Font index {i} is too big. Maximum is 0xffff.")
	return chr(i)


# Reserved (static) glyph characters — DO NOT change the code points, they are alignment-critical.
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

# Misc constants
SQUARE_SIZE: int = 32
FONT_FILE: str = "manual"
BORDER_SIZE: int = 2
HEAVY_WORKBENCH_CATEGORY: str = "__private_heavy_workbench"


# Allocator
@dataclass
class GlyphAllocator:
	""" Owns the dynamic unicode counter and the bitmap font-provider registry.

	This is the single source of truth for ``manual.json`` font providers, replacing the
	v1 ``SharedMemory.font_providers`` / ``SharedMemory.next_craft_font`` globals. All
	mutating methods are guarded by a lock so page preparation can be multithreaded.

	>>> alloc = GlyphAllocator(project_id="test")
	>>> a, b = alloc.allocate(), alloc.allocate()
	>>> a != b
	True
	>>> char = alloc.register_image("test:font/example.png", ascent=8, height=16)
	>>> alloc.register_image("test:font/example.png", ascent=8, height=16) == char  # deduped by file
	True
	>>> alloc.to_font_json()["providers"][0]["file"]
	'test:font/example.png'
	"""

	project_id: str
	""" Namespace of the project owning the font. """
	next_craft_font: int = DEFAULT_NEXT_CRAFT_FONT
	""" Next dynamic code point to hand out (see :meth:`allocate`). """
	providers: list[JsonDict] = field(default_factory=list[JsonDict])
	""" Bitmap providers accumulated for ``manual.json``. """
	lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
	""" Guards the counter and provider list for multithreaded page preparation. """
	_first_char_by_file: dict[str, str] = field(default_factory=dict[str, str], repr=False)
	""" First registered glyph char per provider file (index for :meth:`find_char_by_file`). """

	def allocate(self) -> str:
		""" Reserve and return the next free dynamic glyph character. """
		with self.lock:
			self.next_craft_font += 1
			return get_font(self.next_craft_font)

	def add_provider(self, char: str, file: str, ascent: int, height: int) -> None:
		""" Register a bitmap provider mapping ``char`` to the texture ``file``. """
		with self.lock:
			self.providers.append({"type": "bitmap", "file": file, "ascent": ascent, "height": height, "chars": [char]})
			self._first_char_by_file.setdefault(file, char)

	def find_char_by_file(self, file: str) -> str | None:
		""" Return the glyph char already registered for ``file`` (dedupe), if any. """
		return self._first_char_by_file.get(file)

	def register_image(self, file: str, ascent: int, height: int) -> str:
		""" Allocate a glyph for ``file`` (deduped by file) and register its provider.

		Returns the glyph character.
		"""
		existing: str | None = self.find_char_by_file(file)
		if existing is not None:
			return existing
		char: str = self.allocate()
		self.add_provider(char, file, ascent, height)
		return char

	def to_font_json(self) -> JsonDict:
		""" Build the ``manual.json`` font definition. """
		return {"providers": self.providers}
