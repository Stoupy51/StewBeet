""" PIL helpers shared by every glyph generator. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from PIL import Image, ImageChops, ImageFilter


# Functions
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

