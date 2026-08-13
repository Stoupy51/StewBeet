""" Turning render requests into font glyphs.

One :class:`GlyphAllocator` collects every provider of the build. Each distinct
``(item id, height, ascent, resolution)`` gets its own glyph character, while the textures backing
them are written once per ``(item id, stored pixels)``, so several glyphs can share one image.

A render Minecraft cannot fit in a single glyph (more than 256 texture pixels on a side, or floating
above the baseline) is cut into a grid instead: several glyphs and the spacing putting them back
together, which the text component carries as one string of characters like any other glyph.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass, field

import stouputils as stp
from beet import Texture
from PIL import Image

from ....core.__memory__ import Mem
from ....core.utils.fonts import (
	MAX_GLYPH_SIZE,
	GlyphAllocator,
	SpliceLayout,
	ensure_item_images,
	glyph_advance,
	merge_font_providers,
	opaque_width,
	plan_splice,
)
from ...initialize.project_images import find_pack_png
from .config import (
	ICON_ID,
	TEXTURE_FOLDER,
	TextRendersConfig,
	first_frame_box,
	fitting_resolution,
	scale_to_height,
	to_resource_path,
)
from .confirm import ask_oversized
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
	""" Glyph key -> glyph characters, so the same render costs one provider. """
	chars_by_provider: dict[tuple[str, int, int], str] = field(default_factory=dict[tuple[str, int, int], str])
	""" (texture, ascent, height) -> glyph character. Two requests landing on the same provider share it. """
	written: int = 0
	""" Providers already merged into the font, so calling :meth:`emit` again never duplicates them. """
	oversized: bool | None = None
	""" Answer to the oversized-render question, asked at most once per build. """

	def __post_init__(self) -> None:
		self.allocator = GlyphAllocator(self.config.project_id)

	def texture_name(self, item_id: str, stored: tuple[int, int]) -> str:
		""" Resource pack texture name (relative to ``textures/``) for an item stored at ``stored`` pixels.

		The name follows the stored pixels rather than the displayed height, so the same image shown at
		several heights is only written once. It also goes through :func:`to_resource_path`, without
		which the reserved ``ICON`` id would name a texture Minecraft refuses to load.
		"""
		return f"{TEXTURE_FOLDER}/{to_resource_path(f'{item_id.replace(":", "_")}_{stored[0]}x{stored[1]}')}"

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

	def allow_oversized(self, item_id: str, layout: SpliceLayout) -> bool:
		""" Whether a render too big for one glyph may be cut into several.

		The configured answer wins; without one the question is asked in the terminal and remembered,
		then reused for the rest of the build.
		"""
		if self.config.allow_oversized is not None:
			return self.config.allow_oversized
		if self.oversized is None:
			self.oversized = ask_oversized(item_id, layout.stored, len(layout.tiles))
		return self.oversized

	def warn_capped(self, item_id: str, layout: SpliceLayout, wanted: tuple[int, int]) -> None:
		""" Tell the author when the ascent forced a render to be stored smaller than it asked for.

		Minecraft refuses a glyph whose ascent exceeds its height, so the topmost tile has to span
		from the top of the picture down to the baseline and fit in one glyph on its own. Cutting
		that row thinner does not help, since every row above the baseline still reaches it: only a
		smaller ascent does, which is why the message names the one that would have worked.
		"""
		if layout.stored[1] >= wanted[1]:
			return
		scale: int = max(1, wanted[1] // layout.height)
		stp.warning(
			f"'{item_id}' is stored at {layout.stored[0]}x{layout.stored[1]} instead of {wanted[0]}x{wanted[1]}: "
			f"Minecraft refuses a glyph whose ascent exceeds its height, so the topmost tile has to reach from the top "
			f"of the picture down to the baseline and fit in one {MAX_GLYPH_SIZE}px glyph. Use an ascent of "
			f"{MAX_GLYPH_SIZE // scale} or less (currently {layout.ascent}) to keep {wanted[0]}x{wanted[1]}."
		)

	def provider_char(self, file: str, ascent: int, height: int) -> str:
		""" Glyph character of the ``(file, ascent, height)`` provider, registering it on first use.

		Two renders differing only in ascent are two glyphs sharing one texture, while two that
		resolve identically share the glyph itself.
		"""
		char: str | None = self.chars_by_provider.get((file, ascent, height))
		if char is None:
			char = self.allocator.allocate()
			self.allocator.add_provider(char, file, ascent=ascent, height=height)
			self.chars_by_provider[(file, ascent, height)] = char
		return char

	def prepare(self, opened: Image.Image, frame: tuple[int, int, int, int] | None, size: tuple[int, int]) -> Image.Image:
		""" The source image in RGBA, cropped to its first animation frame and resized to ``size``. """
		image: Image.Image = opened.convert("RGBA")
		if frame is not None:
			image = image.crop(frame)
		if image.size != size:
			image = image.resize(size, Image.Resampling.NEAREST)
		return image

	def single_glyph(
		self, item_id: str, opened: Image.Image, frame: tuple[int, int, int, int] | None, stored: tuple[int, int],
		height: int, ascent: int,
	) -> str:
		""" One glyph showing the whole image, the shape every render small enough to fit takes.

		The stored texture keeps the source aspect ratio: Minecraft has no width to set, it derives
		the on-screen width from the texture itself.
		"""
		assets = Mem.ctx.assets[self.config.project_id]
		name: str = self.texture_name(item_id, stored)
		if name not in assets.textures:
			assets.textures[name] = Texture(self.prepare(opened, frame, stored))
		return self.provider_char(f"{self.config.project_id}:{name}.png", ascent, height)

	def spliced_glyph(
		self, item_id: str, opened: Image.Image, frame: tuple[int, int, int, int] | None, layout: SpliceLayout,
	) -> str:
		""" A grid of glyphs showing one image, with the spacing that puts it back together.

		Each row is drawn left to right, a negative space brings the pen back to the left edge before
		the next one, and the rows hang from decreasing ascents. Every tile is followed by the spacing
		correcting Minecraft's own advance, so the tiles touch without overlapping.

		Args:
			item_id	(str):			Fully qualified item id, used to name the textures.
			opened	(Image.Image):	Source image, still at its original size.
			frame	(tuple | None):	First frame of an animation strip, or None.
			layout	(SpliceLayout):	Grid to cut, from :func:`~stewbeet.core.utils.fonts.plan_splice`.
		Returns:
			str: The glyph characters to write in the text component, in drawing order.
		"""
		namespace: str = self.config.project_id
		assets = Mem.ctx.assets[namespace]
		folder: str = f"{self.texture_name(item_id, layout.stored)}_h{layout.height}a{layout.ascent}"

		# Rows always reach down to the baseline, so an image not touching it is padded with transparency
		source: Image.Image = self.prepare(opened, frame, layout.content)
		if layout.content != layout.stored:
			padded: Image.Image = Image.new("RGBA", layout.stored, (0, 0, 0, 0))
			padded.paste(source, (0, 0))
			source = padded

		parts: list[str] = []
		row: int = 0
		for tile in layout.tiles:
			if tile.row != row:
				parts.append(self.allocator.add_space(-layout.width))
				row = tile.row

			name: str = f"{folder}/r{tile.row}c{tile.column}"
			image: Image.Image = source.crop(tile.box)
			assets.textures.setdefault(name, Texture(image))
			parts.append(self.provider_char(f"{namespace}:{name}.png", tile.ascent, tile.height))

			# Minecraft advances by the visible width of the tile, not by the tile itself
			padding: int = tile.width - glyph_advance(opaque_width(image), layout.scale)
			if padding != 0:
				parts.append(self.allocator.add_space(padding))
		return "".join(parts)

	def emit(self, requests: list[RenderRequest]) -> dict[GlyphKey, str]:
		""" Generate one glyph per distinct request, and write the font.

		Requests whose glyph already exists are skipped, so calling this again only pays for the new
		ones and never re-renders or re-downloads an image.

		Args:
			requests (list[RenderRequest]): Every render node found in the build.
		Returns:
			dict: Glyph key -> glyph characters, missing images left out.
		"""
		missing: list[GlyphKey] = [
			key for key in dict.fromkeys(request.glyph_key for request in requests) if key not in self.glyphs
		]
		if not missing:
			return self.glyphs

		sources: dict[str, str] = self.source_images({key[0] for key in missing})
		for key in missing:
			item_id, height, ascent, resolution = key
			source: str | None = sources.get(item_id)
			if source is None:
				continue

			with Image.open(source) as opened:
				frame: tuple[int, int, int, int] | None = first_frame_box(opened.size)
				native: tuple[int, int] = (frame[2], frame[3]) if frame else opened.size
				stored: tuple[int, int] = scale_to_height(native, resolution) if resolution > 0 else native

				# Too big for one glyph, or floating over the baseline: both are laid out as a grid, which
				# may still come out as a single tile once the resolution is capped to what fits
				layout: SpliceLayout | None = None
				if max(stored) > MAX_GLYPH_SIZE or ascent > height:
					layout = plan_splice(native, height, ascent, resolution)
					if len(layout.tiles) > 1 and not self.allow_oversized(item_id, layout):
						resolution = fitting_resolution(native, MAX_GLYPH_SIZE)
						stored = scale_to_height(native, resolution)
						layout = plan_splice(native, height, ascent, resolution) if ascent > height else None

				if layout is not None:
					self.warn_capped(item_id, layout, stored)
					stored_size: str = f"{layout.stored[0]}x{layout.stored[1]}"
					if len(layout.tiles) > 1:
						self.glyphs[key] = self.spliced_glyph(item_id, opened, frame, layout)
						stp.debug(f"Cut '{item_id}' into a {layout.columns}x{layout.rows} grid of glyphs, stored at {stored_size}")
					elif layout.content != layout.stored:
						self.glyphs[key] = self.spliced_glyph(item_id, opened, frame, layout)
						stp.debug(f"Padded '{item_id}' down to the baseline, stored at {stored_size}")
					else:
						# One tile with nothing to pad is an ordinary glyph, sharing its texture like any other
						self.glyphs[key] = self.single_glyph(item_id, opened, frame, layout.stored, layout.height, layout.ascent)
				else:
					self.glyphs[key] = self.single_glyph(item_id, opened, frame, stored, height, ascent)
			Mem.used_textures.add(stp.clean_path(source))

		# Merge only what this call added, so a second emit() never duplicates providers
		if len(self.allocator.providers) > self.written:
			merge_font_providers(self.config.project_id, self.config.font_name, self.allocator.providers[self.written:])
			self.written = len(self.allocator.providers)
		return self.glyphs

