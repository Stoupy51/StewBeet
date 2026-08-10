""" Turning render requests into font glyphs.

One :class:`GlyphAllocator` collects every provider of the build. Each distinct
``(item id, height, ascent, resolution)`` gets its own glyph character, while the textures backing
them are written once per ``(item id, stored pixels)``, so several glyphs can share one image.
"""
# Imports
from dataclasses import dataclass, field

import stouputils as stp
from beet import Texture
from PIL import Image

from ....core.__memory__ import Mem
from ....core.utils.fonts import GlyphAllocator, ensure_item_images, merge_font_providers
from ...initialize.project_images import find_pack_png
from .config import ICON_ID, TEXTURE_FOLDER, TextRendersConfig, first_frame_box, scale_to_height
from .scan import RenderRequest

# Constants
type GlyphKey = tuple[str, int, int, int]
""" Identity of a glyph: item id, displayed height, ascent, and texture resolution. """


# Classes
@dataclass(slots=True)
class GlyphEmitter:
	""" Allocates a glyph per distinct render request and writes the resulting font.

	>>> emitter = GlyphEmitter(config=TextRendersConfig(project_id="demo"))
	>>> emitter.texture_name("demo:steel_ingot", (16, 16))
	'font/renders/demo_steel_ingot_16x16'
	>>> emitter.texture_name("minecraft:stone", (64, 64))  # named after the stored pixels, not the displayed height
	'font/renders/minecraft_stone_64x64'
	"""
	config: TextRendersConfig
	""" Font name, default height, default resolution and cache flag. """
	allocator: GlyphAllocator = field(init=False)
	""" Collects the providers of every emitted glyph. """
	glyphs: dict[GlyphKey, str] = field(default_factory=dict[GlyphKey, str])
	""" Glyph key -> glyph character, so the same render costs one provider. """
	chars_by_provider: dict[tuple[str, int, int], str] = field(default_factory=dict[tuple[str, int, int], str])
	""" (texture, ascent, height) -> glyph character. Two requests landing on the same provider share it. """
	written: int = 0
	""" Providers already merged into the font, so calling :meth:`emit` again never duplicates them. """

	def __post_init__(self) -> None:
		self.allocator = GlyphAllocator(self.config.project_id)

	def texture_name(self, item_id: str, stored: tuple[int, int]) -> str:
		""" Resource pack texture name (relative to ``textures/``) for an item stored at ``stored`` pixels.

		The name follows the stored pixels rather than the displayed height, so the same image shown at
		several heights is only written once.
		"""
		return f"{TEXTURE_FOLDER}/{item_id.replace(':', '_')}_{stored[0]}x{stored[1]}"

	def source_images(self, item_ids: set[str]) -> dict[str, str]:
		""" Resolve the PNG backing each item, batching the renders and the downloads.

		The reserved ``ICON`` id resolves to the project ``pack.png`` instead of an item.
		"""
		items: set[str] = item_ids - {ICON_ID}
		sources: dict[str, str] = ensure_item_images(items, self.config.cache_assets) if items else {}

		if ICON_ID in item_ids:
			pack_icon: str | None = find_pack_png()
			if pack_icon:
				sources[ICON_ID] = pack_icon
			else:
				stp.warning(f"A render node asks for '{ICON_ID}' but no pack.png was found next to the project")
		return sources

	def emit(self, requests: list[RenderRequest]) -> dict[GlyphKey, str]:
		""" Generate one glyph per distinct request, and write the font.

		Requests whose glyph already exists are skipped, so calling this again only pays for the new
		ones and never re-renders or re-downloads an image.

		Args:
			requests (list[RenderRequest]): Every render node found in the build.
		Returns:
			dict: Glyph key -> glyph character, missing images left out.
		"""
		missing: list[GlyphKey] = [
			key for key in dict.fromkeys(request.glyph_key for request in requests) if key not in self.glyphs
		]
		if not missing:
			return self.glyphs

		sources: dict[str, str] = self.source_images({key[0] for key in missing})
		assets = Mem.ctx.assets[self.config.project_id]

		for key in missing:
			item_id, height, ascent, resolution = key
			source: str | None = sources.get(item_id)
			if source is None:
				continue

			# The stored texture keeps the source aspect ratio: Minecraft has no width to set, it
			# derives the on-screen width from the texture itself
			with Image.open(source) as opened:
				frame: tuple[int, int, int, int] | None = first_frame_box(opened.size)
				native: tuple[int, int] = (frame[2], frame[3]) if frame else opened.size
				stored: tuple[int, int] = scale_to_height(native, resolution) if resolution > 0 else native

				# Write the texture once per (item, stored pixels): several glyph heights can share it
				name: str = self.texture_name(item_id, stored)
				if name not in assets.textures:
					image: Image.Image = opened.convert("RGBA")
					if frame is not None:
						image = image.crop(frame)
					if image.size != stored:
						image = image.resize(stored, Image.Resampling.NEAREST)
					assets.textures[name] = Texture(image)
					Mem.used_textures.add(stp.clean_path(source))

			# One provider per (texture, ascent, height): two nodes differing only in ascent are two
			# glyphs sharing one texture, while two that resolve identically share the glyph itself
			provider: tuple[str, int, int] = (name, ascent, height)
			char: str | None = self.chars_by_provider.get(provider)
			if char is None:
				char = self.allocator.allocate()
				self.allocator.add_provider(char, f"{self.config.project_id}:{name}.png", ascent=ascent, height=height)
				self.chars_by_provider[provider] = char
			self.glyphs[key] = char

		# Merge only what this call added, so a second emit() never duplicates providers
		if len(self.allocator.providers) > self.written:
			merge_font_providers(self.config.project_id, self.config.font_name, self.allocator.providers[self.written:])
			self.written = len(self.allocator.providers)
		return self.glyphs

