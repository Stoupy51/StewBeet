""" Typed configuration for the text renders, read from ``ctx.meta["stewbeet"]["text_renders"]``. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from dataclasses import dataclass

from beet import Context
from stouputils.typing import JsonDict

# Constants
ICON_ID: str = "ICON"
""" Reserved render id resolving to the project ``pack.png`` instead of an item. """

DEFAULT_HEIGHT: int = 16
""" On-screen glyph height in pixels, used when a render node omits its own "height". """

DEFAULT_RESOLUTION: int = 0
""" Texture height used when a render node omits its own "resolution". 0 keeps the source image untouched. """

TEXT_CENTER_ABOVE_BASELINE: int = 3
""" Vertical center of a line of text, in pixels above the baseline.

Minecraft draws its 8px font with ascent 7, so a character spans from 7px above the baseline down to
1px below it, putting the middle of the text band 3px above the baseline.
"""

TEXTURE_FOLDER: str = "font/renders"
""" Resource pack folder, relative to textures/, holding the generated glyphs. """

RESOURCE_PATH_ALLOWED: str = "abcdefghijklmnopqrstuvwxyz0123456789/._-"
""" The only characters Minecraft accepts in the path half of a resource location. """


# Functions
def to_resource_path(name: str) -> str:
	""" Lowercase a generated name and replace anything Minecraft would reject in a resource path.

	Minecraft refuses the whole font, not just the offending glyph, when a provider names a texture
	outside ``[a-z0-9/._-]``: it fails the resource pack reload with "Not a valid resource location".
	The reserved ``ICON`` id is what hits this in practice, since it reaches the texture name as
	written, but any item id carrying an uppercase letter would do the same.

	Args:
		name (str): Candidate path, ex: "ICON_128x128"
	Returns:
		str: The same path, in the characters Minecraft accepts

	Examples:
		>>> to_resource_path("ICON_128x128")
		'icon_128x128'
		>>> to_resource_path("demo_steel_ingot_16x16")
		'demo_steel_ingot_16x16'
		>>> to_resource_path("Weird Name!")
		'weird_name_'
	"""
	return "".join(char if char in RESOURCE_PATH_ALLOWED else "_" for char in name.lower())


# Classes
@dataclass(kw_only=True, slots=True)
class TextRendersConfig:
	""" Typed mirror of the ``text_renders`` stewbeet config block.

	>>> config = TextRendersConfig(project_id="mypack")
	>>> config.font
	'mypack:renders'
	>>> config.default_height
	16
	>>> TextRendersConfig(project_id="mypack", font_name="glyphs").font
	'mypack:glyphs'
	"""
	project_id: str
	""" Namespace the generated font lives in. """
	font_name: str = "renders"
	""" Font file name, without the namespace. """
	default_height: int = DEFAULT_HEIGHT
	""" On-screen glyph height used when a render node omits its own "height". """
	default_resolution: int = DEFAULT_RESOLUTION
	""" Texture height used when a render node omits its own "resolution". 0 keeps the source image untouched. """
	cache_assets: bool = True
	""" Reuse the item PNGs that already exist instead of regenerating them. """
	allow_oversized: bool | None = None
	""" Whether a render too big for one glyph may be cut into several, or None to ask in the terminal. """

	@property
	def font(self) -> str:
		""" Fully-qualified font id, e.g. ``mypack:renders``. """
		return f"{self.project_id}:{self.font_name}"

	@classmethod
	def from_meta(cls, ctx: Context) -> TextRendersConfig:
		""" Build a :class:`TextRendersConfig` from the beet context meta. """
		assert ctx.project_id, "Project ID is not set."
		stewbeet: JsonDict = ctx.meta.get("stewbeet", {})
		raw: JsonDict = stewbeet.get("text_renders", {})
		return cls(
			project_id=ctx.project_id,
			font_name=raw.get("font", "renders"),
			default_height=raw.get("default_height", DEFAULT_HEIGHT),
			default_resolution=raw.get("default_resolution", DEFAULT_RESOLUTION),
			cache_assets=raw.get("cache_assets", stewbeet.get("manual", {}).get("cache_assets", True)),
			allow_oversized=raw.get("allow_oversized", None),
		)


def default_ascent(height: int) -> int:
	""" Baseline offset centering a glyph of ``height`` pixels on the surrounding line of text.

	A bitmap glyph hangs from its ascent: the top sits ``ascent`` pixels above the baseline and the
	bottom ``height - ascent`` pixels below it. Centering its middle on the text band therefore means
	``ascent = height / 2 + 3``, which lands on 7 for an 8px glyph, exactly what vanilla uses.

	Minecraft rejects a provider whose ascent exceeds its height, so tiny glyphs are clamped and end
	up sitting slightly low rather than breaking the pack.

	Args:
		height (int): Height of the glyph in pixels.
	Returns:
		int: Ascent to give the bitmap provider.

	Examples:
		>>> default_ascent(8)  # same as vanilla's 8px font
		7
		>>> default_ascent(10), default_ascent(16), default_ascent(64)
		(8, 11, 35)
		>>> default_ascent(4)  # clamped: ascent may never exceed height
		4
	"""
	return min(height, round(height / 2) + TEXT_CENTER_ABOVE_BASELINE)


def scale_to_height(size: tuple[int, int], height: int) -> tuple[int, int]:
	""" Size of an image scaled to ``height`` pixels tall, keeping its aspect ratio.

	Minecraft scales a bitmap glyph to the provider's height and derives its on-screen width from the
	texture's aspect ratio; there is no width to set. So the stored texture only ever needs scaling,
	never stretching. Item renders are stored untouched by default, and this is what shrinks them when
	a pack would rather trade sharpness at high GUI scales for a smaller download.

	Args:
		size	(tuple[int, int]):	Size of the source image.
		height	(int):				Wanted height in pixels.
	Returns:
		tuple[int, int]: Size to resize the source image to.

	Examples:
		>>> scale_to_height((16, 16), 64)   # square source stays square
		(64, 64)
		>>> scale_to_height((32, 16), 64)   # a 2:1 source keeps its ratio
		(128, 64)
		>>> scale_to_height((16, 16), 16)   # already the right height
		(16, 16)
		>>> scale_to_height((3, 40), 4)     # never collapses to a zero width
		(1, 4)
	"""
	width, source_height = size
	return (max(1, round(width * height / source_height)), height)


def fitting_resolution(size: tuple[int, int], limit: int) -> int:
	""" Largest texture height keeping both sides of an image within ``limit`` pixels.

	This is the fallback for a render whose splicing was turned down: the picture is stored as one
	glyph again, shrunk just enough for Minecraft to display it at all.

	Args:
		size	(tuple[int, int]):	Size of the source image.
		limit	(int):				Largest side allowed, in pixels.
	Returns:
		int: Texture height to store the image at.

	Examples:
		>>> fitting_resolution((1000, 370), 256)  # a wide image is bound by its width
		94
		>>> fitting_resolution((512, 512), 256)
		256
		>>> fitting_resolution((64, 64), 256)     # already small enough to keep untouched
		64
	"""
	width, height = size
	return max(1, min(height, limit, limit * height // width))


def first_frame_box(size: tuple[int, int]) -> tuple[int, int, int, int] | None:
	""" Crop box isolating the first frame of a vertical animation strip.

	An animated Minecraft texture is a column of square frames, so a source taller than it is wide by
	a whole number of frames would otherwise render as a long ribbon. This is the same heuristic
	:mod:`stewbeet.plugins.resource_pack.check_power_of_2` uses to recognise animated textures.

	Args:
		size (tuple[int, int]): Size of the source image.
	Returns:
		tuple[int, int, int, int] | None: Box of the first frame, or None when the image is not a strip.

	Examples:
		>>> first_frame_box((16, 96))  # animated: 6 frames of 16x16
		(0, 0, 16, 16)
		>>> first_frame_box((16, 16)) is None
		True
		>>> first_frame_box((64, 32)) is None  # wider than tall, not a strip
		True
	"""
	width, height = size
	if height > width and height % width == 0:
		return (0, 0, width, width)
	return None

