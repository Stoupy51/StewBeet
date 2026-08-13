""" Cutting an oversized image into the grid of glyphs Minecraft can actually draw.

Minecraft stitches every bitmap glyph into a 256x256 font atlas, and one that fits in no sheet is
drawn as the missing-character box instead, so a bigger picture has to be cut into tiles. Each tile
becomes its own glyph, and the text component puts them back together: the tiles of a row sit side
by side, negative spacing brings the pen back to the left edge, and the next row hangs from a lower
ascent.

Two rules drive the geometry, both taken from the game's own code (``BitmapProvider``, ``FontTexture``
and ``DynamicAtlasTree``):

- ``BitmapProvider.Definition.validate`` rejects a provider whose ascent exceeds its height, which
  means no row may stop above the baseline. The topmost row therefore always reaches down to it, and
  the part of the image standing above the baseline is what caps the resolution: it has to fit in a
  single glyph.
- Spacing is whole pixels only, so tiles line up seamlessly only when each is an exact number of
  screen pixels wide. Hence ``scale``: the stored texture is an integer multiple of the displayed
  size, so cutting on a screen pixel also cuts on a texture pixel.
"""
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import math
from dataclasses import dataclass

from PIL import Image

# Constants
MAX_GLYPH_SIZE: int = 256
""" Largest bitmap glyph Minecraft can stitch into its font atlas, in texture pixels.

``FontTexture`` allocates 256x256 sheets, and its atlas tree hands out a slot of exactly that size
before it starts splitting, so a 256x256 glyph fits (taking a whole sheet) and a 257px one never
does. A glyph no sheet accepts is replaced by the missing-character box.
"""

LETTER_SPACING: int = 1
""" Pixels Minecraft adds to the advance of every bitmap glyph, on top of its measured width. """


# Classes
@dataclass(frozen=True, slots=True)
class SpliceTile:
	""" One cell of a spliced render: a crop of the stored texture, and where it lands on screen. """

	row: int
	""" Index of the tile row, 0 being the topmost. """
	column: int
	""" Index of the tile column, 0 being the leftmost. """
	box: tuple[int, int, int, int]
	""" Crop box inside the stored texture: left, top, right, bottom. """
	width: int
	""" On-screen width of the tile in pixels. """
	ascent: int
	""" Baseline offset of the row this tile belongs to. """
	height: int
	""" On-screen height of the row this tile belongs to. """


@dataclass(frozen=True, slots=True)
class SpliceLayout:
	""" How an oversized image is cut into glyph-sized tiles, and how big they are on screen. """

	tiles: tuple[SpliceTile, ...]
	""" Every tile, in reading order: left to right, top row first. """
	content: tuple[int, int]
	""" Size the source image must be resized to. """
	stored: tuple[int, int]
	""" Size of the texture the tiles are cut out of, the content padded down to the baseline. """
	width: int
	""" Total on-screen width of the reassembled image, in pixels. """
	height: int
	""" Total on-screen height of the image, in pixels. """
	ascent: int
	""" Pixels between the top of the image and the text baseline, clamped to what is representable. """
	scale: int
	""" Texture pixels per on-screen pixel. """
	columns: int
	""" Number of tiles per row. """
	rows: int
	""" Number of tile rows. """


# Functions
def split_evenly(total: int, parts: int) -> tuple[int, ...]:
	""" Cut ``total`` pixels into ``parts`` slices differing by at most one pixel.

	Args:
		total	(int):	Number of pixels to share out.
		parts	(int):	Number of slices to cut.
	Returns:
		tuple[int, ...]: Width of each slice, summing back to ``total``.

	Examples:
		>>> split_evenly(100, 4)
		(25, 25, 25, 25)
		>>> split_evenly(10, 3)
		(3, 4, 3)
		>>> split_evenly(7, 1)
		(7,)
	"""
	cuts: list[int] = [round(index * total / parts) for index in range(parts + 1)]
	return tuple(cuts[index + 1] - cuts[index] for index in range(parts))


def glyph_advance(opaque: int, scale: int) -> int:
	""" Pixels Minecraft moves the pen by after drawing a bitmap glyph.

	It measures the glyph up to its rightmost non-transparent column, scales that down to the
	displayed size rounding halves up, then adds one pixel of letter spacing. Transparent columns on
	the right therefore shorten the advance, which is exactly why the spacing corrections have to be
	computed from the tile images rather than from their nominal widths.

	Args:
		opaque	(int):	Width of the tile up to its last non-transparent column, in texture pixels.
		scale	(int):	Texture pixels per on-screen pixel.
	Returns:
		int: Advance in on-screen pixels.

	Examples:
		>>> glyph_advance(256, 16)  # a tile whose content reaches its right edge
		17
		>>> glyph_advance(0, 16)    # a fully transparent tile still advances the letter spacing
		1
		>>> glyph_advance(24, 16)   # 1.5 rounds up, never to even
		3
	"""
	return math.floor(0.5 + opaque / scale) + LETTER_SPACING


def opaque_width(image: Image.Image) -> int:
	""" Index just past the rightmost column of ``image`` holding a non-transparent pixel.

	Only the alpha channel is looked at, mirroring what Minecraft measures: a column of invisible
	pixels counts as empty whatever color it carries.

	Args:
		image (Image.Image): Tile image, in RGBA.
	Returns:
		int: Width of the visible part, 0 when the tile is fully transparent.

	Examples:
		>>> from PIL import Image
		>>> opaque_width(Image.new("RGBA", (16, 16), (255, 0, 0, 255)))
		16
		>>> opaque_width(Image.new("RGBA", (16, 16), (255, 0, 0, 0)))
		0
	"""
	box: tuple[int, int, int, int] | None = image.getchannel("A").getbbox()
	return box[2] if box else 0


def plan_splice(native: tuple[int, int], height: int, ascent: int, resolution: int = 0, limit: int = MAX_GLYPH_SIZE) -> SpliceLayout:
	""" Work out the grid an image has to be cut into to be displayed at ``height`` pixels tall.

	The stored texture is snapped to an integer multiple of the displayed size so every cut lands on
	a whole texture pixel. That multiple comes from ``resolution`` when one is asked for, and from
	the source image otherwise, then shrinks as needed to keep the part standing above the baseline
	within one glyph.

	Args:
		native		(tuple[int, int]):	Size of the source image.
		height		(int):				On-screen height of the whole image, in pixels.
		ascent		(int):				Pixels between the top of the image and the text baseline.
		resolution	(int):				Wanted texture height, or 0 to follow the source image.
		limit		(int):				Largest glyph Minecraft can display, in texture pixels.
	Returns:
		SpliceLayout: Tiles to cut, and the size the source must be resized to first.

	Examples:
		>>> layout = plan_splice((1000, 370), height=37, ascent=21)
		>>> layout.stored, layout.width, layout.scale   # a 10:1 image kept at its native pixels
		((1000, 370), 100, 10)
		>>> layout.columns, layout.rows
		(4, 2)
		>>> layout.tiles[0]   # the top row stops on the baseline, 21 pixels below the top
		SpliceTile(row=0, column=0, box=(0, 0, 250, 210), width=25, ascent=21, height=21)
		>>> layout.tiles[4]   # the row below it hangs from the baseline
		SpliceTile(row=1, column=0, box=(0, 210, 250, 370), width=25, ascent=0, height=16)
		>>> max(tile.box[2] - tile.box[0] for tile in layout.tiles) <= 256
		True

		A picture only too wide is cut into columns alone, keeping a single row:

		>>> plan_splice((512, 64), height=16, ascent=11).rows
		1
		>>> plan_splice((512, 64), height=16, ascent=11).columns
		2

		An ascent above the height floats the image over the baseline, padding what is missing:

		>>> plan_splice((16, 16), height=8, ascent=20).stored   # 8x8 of content, padded down to the baseline
		(16, 40)
	"""
	# More than a full glyph above the baseline is not representable, whatever the resolution
	ascent = min(ascent, limit)
	width: int = max(1, round(native[0] * height / native[1]))
	bottom: int = max(height, ascent)
	scale: int = max(1, round(resolution / height) if resolution > 0 else native[1] // height)

	# The topmost row reaches down to the baseline, so what stands above it has to fit in one glyph
	above: int = min(ascent, bottom) if ascent > 0 else 0
	if bottom * scale > limit and above > 0:
		scale = max(1, min(scale, limit // above))

	cuts: list[int] = [0]
	if bottom * scale <= limit:
		cuts.append(bottom)
	else:
		if above > 0:
			cuts.append(above)
		step: int = max(1, limit // scale)
		while cuts[-1] < bottom:
			cuts.append(min(cuts[-1] + step, bottom))

	columns: int = max(1, math.ceil(width / max(1, limit // scale)))
	widths: tuple[int, ...] = split_evenly(width, columns)

	tiles: list[SpliceTile] = []
	for row in range(len(cuts) - 1):
		top, low = cuts[row], cuts[row + 1]
		left: int = 0
		for column, tile_width in enumerate(widths):
			tiles.append(SpliceTile(
				row=row,
				column=column,
				box=(left * scale, top * scale, (left + tile_width) * scale, low * scale),
				width=tile_width,
				ascent=ascent - top,
				height=low - top,
			))
			left += tile_width
	return SpliceLayout(
		tiles=tuple(tiles),
		content=(width * scale, height * scale),
		stored=(width * scale, bottom * scale),
		width=width,
		height=height,
		ascent=ascent,
		scale=scale,
		columns=columns,
		rows=len(cuts) - 1,
	)

