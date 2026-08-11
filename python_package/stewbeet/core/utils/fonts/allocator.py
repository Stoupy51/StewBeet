""" Unicode glyph allocation for Minecraft bitmap fonts.

Every visual element rendered inside a text component (item icon, recipe template, page background,
invisible spacer) is a PNG mapped to a character inside a Minecraft bitmap font. This module owns the
counter handing out those characters and the provider registry backing the generated font JSON.
"""
# Imports
import threading
from dataclasses import dataclass, field

import stouputils as stp
from stouputils.typing import JsonDict


# Functions
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


# Classes
@dataclass(slots=True)
class GlyphAllocator:
	""" Owns the dynamic unicode counter and the bitmap font-provider registry.

	This is the single source of truth for a generated font's providers. All mutating methods are
	guarded by a lock so callers can prepare their glyphs from several threads.

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
	next_craft_font: int = 0x8000
	""" Next dynamic code point to hand out (see :meth:`allocate`). """
	providers: list[JsonDict] = field(default_factory=list[JsonDict])
	""" Bitmap providers accumulated for the generated font JSON. """
	lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
	""" Guards the counter and provider list for multithreaded glyph preparation. """
	first_char_by_file: dict[str, str] = field(default_factory=dict[str, str], repr=False)
	""" First registered glyph char per provider file (index for :meth:`find_char_by_file`). """
	space_chars: dict[int, str] = field(default_factory=dict[int, str], repr=False)
	""" Advance in pixels -> glyph char, for the characters handed out by :meth:`add_space`. """
	space_provider: JsonDict | None = field(default=None, repr=False)
	""" The single ``space`` provider collecting those characters, created on first use. """

	def allocate(self) -> str:
		""" Reserve and return the next free dynamic glyph character. """
		with self.lock:
			self.next_craft_font += 1
			return get_font(self.next_craft_font)

	def add_provider(self, char: str, file: str, ascent: int, height: int) -> None:
		""" Register a bitmap provider mapping ``char`` to the texture ``file``. """
		with self.lock:
			self.providers.append({"type": "bitmap", "file": file, "ascent": ascent, "height": height, "chars": [char]})
			self.first_char_by_file.setdefault(file, char)

	def add_space(self, advance: int) -> str:
		""" Return a glyph char drawing nothing and moving the pen by ``advance`` pixels.

		Negative advances are how a spliced image gets put back together: they bring the pen back to
		the left edge before the next row is drawn. All of them share one ``space`` provider, and the
		same advance always hands back the same character.

		>>> alloc = GlyphAllocator(project_id="test")
		>>> back = alloc.add_space(-64)
		>>> alloc.add_space(-64) == back  # deduped by advance
		True
		>>> alloc.to_font_json()["providers"][0]["advances"][back]
		-64
		"""
		existing: str | None = self.space_chars.get(advance)
		if existing is not None:
			return existing

		char: str = self.allocate()
		with self.lock:
			if (raced := self.space_chars.get(advance)) is not None:
				return raced
			if self.space_provider is None:
				self.space_provider = {"type": "space", "advances": {}}
				self.providers.append(self.space_provider)
			self.space_provider["advances"][char] = advance
			self.space_chars[advance] = char
		return char

	def find_char_by_file(self, file: str) -> str | None:
		""" Return the glyph char already registered for ``file`` (dedupe), if any. """
		return self.first_char_by_file.get(file)

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
		""" Build the font definition holding every registered provider. """
		return {"providers": self.providers}

