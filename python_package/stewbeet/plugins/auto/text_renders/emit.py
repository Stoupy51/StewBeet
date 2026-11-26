""" Turning render requests into font glyphs.

One :class:`GlyphAllocator` collects every provider of the build. Each distinct
``(item id, height, ascent, resolution, offsets)`` gets its own glyph characters, while the textures backing
them are written once per ``(item id, stored pixels)``, so several glyphs can share one image.

A render Minecraft cannot fit in a single glyph (more than 256 texture pixels on a side,
or floating above the baseline) is cut into a grid instead: several glyphs and the spacing putting them back together,
which the text component carries as one string of characters like any other glyph.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
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
	write_spliced_glyphs,
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
from .scan import IMAGE_SUFFIX, RenderRequest

# Constants
type GlyphKey = tuple[str, int, int, int, int, int | None]
""" Identity of a glyph: item id, displayed height, ascent, texture resolution, offset and offset after. """


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

		The name follows the stored pixels rather than the displayed height,
		so the same image shown at several heights is only written once. It also goes through :func:`to_resource_path`,
		without which the reserved ``ICON`` id would name a texture Minecraft refuses to load.
		"""
		stem: str = item_id.removesuffix(IMAGE_SUFFIX).replace(":", "_")
		return f"{TEXTURE_FOLDER}/{to_resource_path(f'{stem}_{stored[0]}x{stored[1]}')}"

	def source_images(self, item_ids: set[str]) -> dict[str, str]:
		""" Resolve the PNG backing each item, batching the renders and the downloads.

		The reserved ``ICON`` id resolves to the project ``pack.png`` instead of an item,
		and an id ending with ``.png`` to that file under ``textures_folder``, or at the path as written.
		"""
		pictures: set[str] = {item_id for item_id in item_ids if item_id.endswith(IMAGE_SUFFIX)}
		items: set[str] = item_ids - {ICON_ID} - pictures
		sources: dict[str, str] = ensure_item_images(items, self.config.cache_assets) if items else {}

		textures_folder: str = Mem.ctx.meta["stewbeet"]["textures_folder"]
		for picture in pictures:
			path: str = next((p for p in (f"{textures_folder}/{picture}", picture) if os.path.isfile(p)), "")
			if path:
				sources[picture] = path
			else:
				stp.warning(f"A render node asks for the picture '{picture}', found neither under '{textures_folder}' nor as a path")

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

		Minecraft refuses a glyph whose ascent exceeds its height, so the topmost tile has to span from the top of the picture down to
		the baseline and fit in one glyph on its own. Cutting that row thinner does not help,
		since every row above the baseline still reaches it: only a smaller ascent does,
		which is why the message names the one that would have worked.
		Snapping to a whole multiple of the displayed height is not a cap, so it stays silent.
		"""
		scale: int = max(1, wanted[1] // layout.height)
		if layout.scale >= scale:
			return
		stp.warning(
			f"'{item_id}' is stored at {layout.stored[0]}x{layout.stored[1]} instead of {wanted[0]}x{wanted[1]}: "
			f"Minecraft refuses a glyph whose ascent exceeds its height, so the topmost tile has to reach from the top "
			f"of the picture down to the baseline and fit in one {MAX_GLYPH_SIZE}px glyph. Use an ascent of "
			f"{MAX_GLYPH_SIZE // scale} or less (currently {layout.ascent}) to keep {wanted[0]}x{wanted[1]}."
		)

	def provider_char(self, file: str, ascent: int, height: int) -> str:
		""" Glyph character of the ``(file, ascent, height)`` provider, registering it on first use.

		Two renders differing only in ascent are two glyphs sharing one texture,
		while two that resolve identically share the glyph itself.
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

		The stored texture keeps the source aspect ratio: Minecraft has no width to set,
		it derives the on-screen width from the texture itself.
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

		Args:
			item_id: Fully qualified item id, used to name the textures.
			opened:  Source image, still at its original size.
			frame:   First frame of an animation strip, or None.
			layout:  Grid to cut, from :func:`~stewbeet.core.utils.fonts.plan_splice`.
		"""
		folder: str = f"{self.texture_name(item_id, layout.stored)}_h{layout.height}a{layout.ascent}"
		source: Image.Image = self.prepare(opened, frame, layout.content)
		return write_spliced_glyphs(self.allocator, self.config.project_id, folder, source, layout)

	def emit(self, requests: list[RenderRequest]) -> dict[GlyphKey, str]:
		""" Generate one glyph per distinct request, and write the font.

		Requests whose glyph already exists are skipped, so calling this again only pays for the new
		ones and never re-renders or re-downloads an image.

		Args:
			requests: Every render node found in the build.
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
			source: str | None = sources.get(key[0])
			if source is None:
				continue
			with Image.open(source) as opened:
				glyph, advance_error = self.render_glyph(key, opened)
			self.glyphs[key] = self.with_offsets(glyph, advance_error, offset=key[4], offset_after=key[5])
			Mem.used_textures.add(stp.clean_path(source))

		# Merge only what this call added, so a second emit() never duplicates providers
		if len(self.allocator.providers) > self.written:
			merge_font_providers(self.config.project_id, self.config.font_name, self.allocator.providers[self.written:])
			self.written = len(self.allocator.providers)
		return self.glyphs

	def with_offsets(self, glyph: str, advance_error: int, offset: int, offset_after: int | None) -> str:
		""" A glyph wrapped in the spaces moving the pen before it, and after it when ``offset_after`` is given.

		``advance_error`` is how far Minecraft's own advance ends past the right edge of the picture,
		so ``offset_after`` counts from that edge whatever the transparent columns of the image are.
		"""
		before: str = self.allocator.add_space(offset) if offset else ""
		after: int = 0 if offset_after is None else offset_after - advance_error
		return before + glyph + (self.allocator.add_space(after) if after else "")

	def advance_error(self, opened: Image.Image, frame: tuple[int, int, int, int] | None, size: tuple[int, int], height: int) -> int:
		""" Pixels Minecraft's advance ends past the displayed width of a picture drawn from a texture of ``size`` pixels. """
		opaque: int = opaque_width(self.prepare(opened, frame, size))
		return glyph_advance(opaque, size[1] / height) - round(size[0] * height / size[1])

	def render_glyph(self, key: GlyphKey, opened: Image.Image) -> tuple[str, int]:
		""" The characters drawing one requested image, and how far their advance ends past its right edge.

		One glyph, or a grid of them when too big or floating over the baseline, which advances like the single glyph would.
		"""
		item_id, height, ascent, resolution = key[:4]
		frame: tuple[int, int, int, int] | None = first_frame_box(opened.size)
		native: tuple[int, int] = (frame[2], frame[3]) if frame else opened.size
		layout, stored = self.fitted_layout(item_id, native, height, ascent, resolution)
		if layout is None:
			glyph: str = self.single_glyph(item_id, opened, frame, stored, height, ascent)
			return glyph, self.advance_error(opened, frame, stored, height)

		self.warn_capped(item_id, layout, stored)
		stored_size: str = f"{layout.stored[0]}x{layout.stored[1]}"
		if len(layout.tiles) > 1:
			glyph = self.spliced_glyph(item_id, opened, frame, layout)
			stp.debug(f"Cut '{item_id}' into a {layout.columns}x{layout.rows} grid of glyphs, stored at {stored_size}")
		elif layout.content != layout.stored:
			glyph = self.spliced_glyph(item_id, opened, frame, layout)
			stp.debug(f"Padded '{item_id}' down to the baseline, stored at {stored_size}")
		else:
			# One tile with nothing to pad is an ordinary glyph, sharing its texture like any other
			glyph = self.single_glyph(item_id, opened, frame, layout.stored, layout.height, layout.ascent)
		return glyph, self.advance_error(opened, frame, layout.content, layout.height)

	def fitted_layout(
		self, item_id: str, native: tuple[int, int], height: int, ascent: int, resolution: int
	) -> tuple[SpliceLayout | None, tuple[int, int]]:
		""" The grid an image is cut into and the size it is stored at, no grid when one glyph holds it on the baseline.

		Too big for one glyph, or floating over the baseline, both make a grid, which may still come out as a single tile
		once an image that may not stay oversized has its resolution capped to what fits.
		"""
		stored: tuple[int, int] = scale_to_height(native, resolution) if resolution > 0 else native
		if max(stored) <= MAX_GLYPH_SIZE and ascent <= height:
			return None, stored
		layout: SpliceLayout | None = plan_splice(native, height, ascent, resolution)
		if len(layout.tiles) > 1 and not self.allow_oversized(item_id, layout):
			resolution = fitting_resolution(native, MAX_GLYPH_SIZE)
			stored = scale_to_height(native, resolution)
			layout = plan_splice(native, height, ascent, resolution) if ascent > height else None
		return layout, stored

