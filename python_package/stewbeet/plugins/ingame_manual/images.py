"""All PIL image generation for the manual, encapsulated in :class:`GlyphImageBuilder`.

Ports the v1 ``image_utils`` + ``page_font`` modules into instance methods that read from
an injected :class:`~.config.ManualConfig` and write glyph providers through an injected
:class:`~.glyphs.GlyphAllocator` (no more global ``SharedMemory``). Also adds the new
texture-page helpers (:meth:`bake_text_onto`, :meth:`register_full_page_glyph`).
"""

# pyright: reportUnknownMemberType=false
# Imports
import os
from dataclasses import dataclass, field

import stouputils as stp
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from stouputils.typing import JsonDict

from ...core.cls.ingredients import Ingr
from .config import ManualConfig
from .glyphs import (
	BORDER_SIZE,
	MICRO_NONE_FONT,
	SQUARE_SIZE,
	WIKI_INGR_OF_CRAFT_FONT,
	GlyphAllocator,
)
from .paths import template_path


@dataclass(kw_only=True)
class BakedText:
	""" A piece of text to draw directly onto a :class:`~.pages.texture_page.TexturePage` background.

	>>> bt = BakedText(text="Step 1", xy=(10, 20))
	>>> bt.xy
	(10, 20)
	"""
	text: str
	xy: tuple[int, int]
	color: tuple[int, int, int, int] = (0, 0, 0, 255)
	font_size: int = 16
	font_path: str | None = None  # Defaults to the bundled minecraft_font.ttf
	align: str = "left"  # "left" | "center" | "right"
	shadow: tuple[int, int, int, int] | None = None  # Optional shadow color


def lighten_color(color_hex: int, factor: float = 1.42) -> tuple[int, int, int, int]:
	""" Lighten a packed RGB color by a factor and return RGBA.

	>>> lighten_color(0x803721)
	(182, 78, 47, 255)
	"""
	r = (color_hex >> 16) & 0xFF
	g = (color_hex >> 8) & 0xFF
	b = color_hex & 0xFF
	r = min(255, round(r * factor))
	g = min(255, round(g * factor))
	b = min(255, round(b * factor))
	return (r, g, b, 255)


def careful_resize(image: Image.Image, max_result_size: int, resampling: Image.Resampling = Image.Resampling.NEAREST) -> Image.Image:
	""" Resize an image while keeping the aspect ratio.

	>>> careful_resize(Image.new("RGBA", (64, 32)), 32).size
	(32, 16)
	>>> careful_resize(Image.new("RGBA", (16, 64)), 32).size
	(8, 32)
	"""
	if image.size[0] >= image.size[1]:
		factor = max_result_size / image.size[0]
		return image.resize((max_result_size, int(image.size[1] * factor)), resampling)
	else:
		factor = max_result_size / image.size[1]
		return image.resize((int(image.size[0] * factor), max_result_size), resampling)


def ensure_rgba_color(c: tuple[int, ...]) -> tuple[int, int, int, int]:
	""" Ensure the color is in RGBA format.

	>>> ensure_rgba_color((10, 20, 30))
	(10, 20, 30, 255)
	>>> ensure_rgba_color((10, 20, 30, 40))
	(10, 20, 30, 40)
	"""
	if len(c) == 3:
		return (c[0], c[1], c[2], 255)
	if len(c) == 4:
		return c  # type: ignore[return-value]
	raise ValueError("border_color must be (R,G,B) or (R,G,B,A)")


def add_border(image: Image.Image, border_color: tuple[int, int, int, int], border_size: int) -> Image.Image:
	""" Add a colored border around the opaque region of an image (alpha dilation). """
	if border_size <= 0:
		return image
	image = image.convert("RGBA")
	border_color = ensure_rgba_color(border_color)
	filt_size = border_size * 2 + 1
	alpha = image.split()[3]
	dilated = alpha.filter(ImageFilter.MaxFilter(filt_size))
	border_mask = ImageChops.difference(dilated, alpha)
	if not border_mask.getbbox():
		return image
	border_layer = Image.new("RGBA", image.size, border_color)
	out = image.copy()
	out.paste(border_layer, (0, 0), border_mask)
	return out


@dataclass
class GlyphImageBuilder:
	""" Builds every manual texture and registers its glyph provider.

	Holds a reference to the config and the glyph allocator; all paths/flags come from
	those instead of globals.

	>>> config = ManualConfig(project_id="demo", project_name="Demo", project_author="me", cache_path="cache")
	>>> builder = GlyphImageBuilder(config, GlyphAllocator(project_id="demo"))
	>>> builder.image_count(5).size  # Minecraft-style count overlay, always 32x32
	(32, 32)
	"""

	# Expose the module-level PIL helpers as methods so other modules (e.g. recipes/types/*) can
	# reach them through ``r.images.*`` at runtime without importing this module (avoids cycles).
	careful_resize = staticmethod(careful_resize)
	add_border = staticmethod(add_border)

	config: ManualConfig
	""" The manual configuration (paths, resolution flags...). """
	glyphs: GlyphAllocator
	""" Where generated textures register their font providers. """
	_border_color: tuple[int, int, int, int] | None = None
	""" Cache for :meth:`get_border_color`. """
	_wiki_icons_generated: set[str] = field(default_factory=set[str])
	""" Wiki icon files already generated this build (skip re-encoding identical PNGs). """
	_spacer_chars: dict[int, str] = field(default_factory=dict[int, str])
	""" Invisible spacer glyph per pixel width (see :meth:`invisible_spacer`). """

	# --- helpers ---
	def get_border_color(self) -> tuple[int, int, int, int]:
		""" Border color from the top-right pixel of the case template, lightened (cached). """
		if self._border_color is None:
			img = Image.open(template_path("simple_case_no_border.png"))
			width = img.size[0]
			pixel = img.getpixel((width - 1, 0))
			if isinstance(pixel, tuple) and len(pixel) >= 3:
				color_hex = (pixel[0] << 16) | (pixel[1] << 8) | pixel[2]
			else:
				color_hex = 0x803721
			self._border_color = lighten_color(color_hex)
		return self._border_color

	def load_simple_case_no_border(self, high_res: bool) -> Image.Image:
		""" Load the case template, widened by one pixel column in high-res mode. """
		img = Image.open(template_path("simple_case_no_border.png"))
		if not high_res:
			return img
		middle_x = img.size[0] // 2
		result = Image.new("RGBA", (img.size[0] + 1, img.size[1]))
		result.paste(img, (0, 0))
		img = img.crop((middle_x, 0, img.size[0], img.size[1]))
		result.paste(img, (middle_x + 1, 0))
		return result

	def image_count(self, count: int | str) -> Image.Image:
		""" Generate a 32x32 image showing an item count (Minecraft inventory style). """
		count = str(count)
		img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
		draw = ImageDraw.Draw(img)
		font_size: int = 16 if len(count) < 3 else 8
		font = ImageFont.truetype(template_path("minecraft_font.ttf"), size=font_size)
		text_width = draw.textlength(count, font=font)
		text_height = font_size + 4
		shadow_offset: int = 0 if font_size == 16 else 1
		height_offset: int = 0 if font_size == 16 else 3
		pos_1 = (34 - text_width - shadow_offset), (32 - text_height - shadow_offset + height_offset)
		pos_2 = (32 - text_width), (30 - text_height + height_offset)
		draw.text(pos_1, count, (50, 50, 50), font=font)
		draw.text(pos_2, count, (255, 255, 255), font=font)
		return img

	# --- glyph-producing builders ---
	def high_res_icon(self, item: str, item_image: Image.Image, count: int | str | JsonDict = 1) -> str:
		""" Generate a 256px item glyph (with optional count) and return its font string. """
		if isinstance(count, dict):
			count = f"{count.get('min', 1)}-{count.get('max', 1)}"
		item = f"{item}_{str(count).replace('-', '_')}" if isinstance(count, str) or count > 1 else item

		path = f"{self.config.cache_path}/font/high_res/{item}.png"
		provider_path = f"{self.config.project_id}:font/high_res/{item}.png"
		existing: str | None = self.glyphs.find_char_by_file(provider_path)
		if existing is not None:
			return MICRO_NONE_FONT + existing
		font: str = self.glyphs.allocate()
		self.glyphs.add_provider(font, provider_path, ascent=7, height=16)

		os.makedirs(os.path.dirname(path), exist_ok=True)
		high_res: int = 256
		resized = careful_resize(item_image, high_res).convert("RGBA")
		if isinstance(count, str) or count > 1:
			img_count = careful_resize(self.image_count(count), high_res)
			resized.paste(img_count, (0, 0), img_count)
		total_width = resized.size[0] - 1
		total_height = resized.size[1] - 1
		for angle in [(0, 0), (total_width, 0), (0, total_height), (total_width, total_height)]:
			resized.putpixel(angle, (0, 0, 0, 100))
		resized.save(path)
		return MICRO_NONE_FONT + font

	def load_square_texture(self, path_id: str) -> Image.Image:
		""" Load an item texture by ``ns/item`` path id, resized to SQUARE_SIZE (placeholder if missing). """
		ipath = f"{self.config.cache_path}/items/{path_id}.png"
		if not os.path.exists(ipath):
			stp.warning(f"Missing texture at '{ipath}', using placeholder texture")
			texture = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), (255, 255, 255, 0))
		else:
			texture = Image.open(ipath)
		return careful_resize(texture, SQUARE_SIZE)

	def load_result_texture(self, name: str, craft: JsonDict) -> tuple[Image.Image, Image.Image]:
		""" Load + resize a craft's result texture (or the item's own), return (texture, alpha mask). """
		path_id = f"{self.config.project_id}/{name}"
		if craft.get("result"):
			path_id = Ingr(craft["result"]).to_id().replace(":", "/")
		result_texture = self.load_square_texture(path_id)
		return result_texture, result_texture.convert("RGBA").split()[3]

	def recipe_image(self, name: str, page_font: str, output_name: str = "") -> None:
		""" Generate the single-item box image (item with no recipe). Per-recipe-type images are
		produced by each renderer's ``build_image`` under :mod:`..recipes.types`. """
		output_filename = output_name or name
		cache_path = self.config.cache_path
		project_id = self.config.project_id

		image_path = f"{cache_path}/items/{project_id}/{name}.png"
		if not os.path.exists(image_path):
			stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
			result_texture = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), (255, 255, 255, 0))
		else:
			result_texture = Image.open(image_path)

		template = Image.open(template_path("simple_case_no_border.png"))
		factor: int = 1
		if self.config.high_resolution:
			factor_float: float = 256 / template.size[0]
			result_texture = careful_resize(result_texture, round(SQUARE_SIZE * factor_float))
			template = careful_resize(template, 256)
			result_mask = result_texture.convert("RGBA").split()[3]
			factor = int(factor_float)
		else:
			result_texture = careful_resize(result_texture, SQUARE_SIZE)
			result_mask = result_texture.convert("RGBA").split()[3]
		self.glyphs.add_provider(page_font, f"{project_id}:font/page/{output_filename}.png", ascent=0 if not output_name else 6, height=40)
		template.paste(result_texture, (2 * factor, 2 * factor), result_mask)
		template = add_border(template, self.get_border_color(), BORDER_SIZE)
		template.save(f"{cache_path}/font/page/{output_filename}.png")

	def wiki_result_icon(self, name: str, craft: JsonDict) -> str:
		""" Generate a small recipe-result wiki icon and return its font (or default font). """
		font = WIKI_INGR_OF_CRAFT_FONT
		if not craft.get("result"):
			return font
		try:
			craft_type = craft["type"]
			result_item: str = Ingr(craft["result"]).to_id().replace(":", "/")
			texture_path = f"{self.config.cache_path}/items/{result_item}.png"
			result_item = result_item.replace("/", "_")
			dest_path = f"{self.config.cache_path}/font/wiki_icons/{result_item}_{craft_type}.png"

			# Same (result, craft type) pairs produce the same file: only encode the PNG once
			# per build (glyph allocation below is unchanged so the output stays identical).
			if dest_path not in self._wiki_icons_generated:
				item_texture = Image.open(texture_path)
				item_res = 64 if not self.config.high_resolution else 256
				item_res_adjusted = int(item_res * 0.75)
				item_texture = careful_resize(item_texture, item_res_adjusted).convert("RGBA")

				filename: str = "wiki_ingredient_of_craft_template.png" if craft_type != "mining" else "wiki_mining_template.png"
				template = Image.open(template_path(filename))
				template = careful_resize(template, item_res)
				offset = (item_res - item_res_adjusted) // 2
				template.paste(item_texture, (offset, offset), item_texture)
				template.save(dest_path)
				self._wiki_icons_generated.add(dest_path)

			font = self.glyphs.allocate()
			rel_path: str = dest_path.replace(f"{self.config.cache_path}/", f"{self.config.project_id}:")
			self.glyphs.add_provider(font, rel_path, ascent=8, height=16)
		except Exception as e:
			stp.warning(f"Failed to generate craft icon for {name}: {e}\nreturning default font...")
		return font

	# --- new texture-page helpers ---
	def invisible_spacer(self, width_px: int) -> str:
		""" Return an invisible glyph advancing exactly ``width_px`` pixels ("" if <= 0).

		The square ``none`` texture rendered at height ``H`` advances ``H + 1`` pixels, so one
		provider (ascent 0, height ``width_px - 1``) is registered per distinct width, then reused.
		Used by :class:`~.pages.texture_page.TexturePage` left/right paddings.
		"""
		if width_px <= 0:
			return ""
		char: str | None = self._spacer_chars.get(width_px)
		if char is None:
			char = self.glyphs.allocate()
			self.glyphs.add_provider(char, f"{self.config.project_id}:font/none.png", ascent=0, height=width_px - 1)
			self._spacer_chars[width_px] = char
		return char

	def bake_text_onto(self, background: Image.Image, baked_texts: list[BakedText]) -> Image.Image:
		""" Draw a list of :class:`BakedText` onto a copy of ``background`` and return it. """
		out = background.convert("RGBA").copy()
		draw = ImageDraw.Draw(out)
		for bt in baked_texts:
			font_path = bt.font_path or template_path("minecraft_font.ttf")
			font = ImageFont.truetype(font_path, size=bt.font_size)
			x, y = bt.xy
			if bt.align in ("center", "right"):
				w = draw.textlength(bt.text, font=font)
				x = int(x - (w / 2 if bt.align == "center" else w))
			if bt.shadow is not None:
				draw.text((x + 1, y + 1), bt.text, bt.shadow, font=font)
			draw.text((x, y), bt.text, bt.color, font=font)
		return out

	def register_full_page_glyph(self, image: Image.Image, name: str, ascent: int = 1, height: int = 131) -> str:
		""" Save a full-page image under font/page/ and register it as a single glyph.

		Returns the glyph character. Used by :class:`~.pages.texture_page.TexturePage`.
		"""
		os.makedirs(f"{self.config.cache_path}/font/page", exist_ok=True)
		dest = f"{self.config.cache_path}/font/page/{name}.png"
		image.save(dest)
		font = self.glyphs.allocate()
		self.glyphs.add_provider(font, f"{self.config.project_id}:font/page/{name}.png", ascent=ascent, height=height)
		return font
