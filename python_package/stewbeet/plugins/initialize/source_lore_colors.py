
# Imports
import colorsys
import math
from collections import Counter

import stouputils as stp
from PIL import Image, ImageColor

from ...core import Mem

# Logo pixels below these thresholds count as gray/black and are ignored, the rest is grouped by hue
MIN_SATURATION: float = 0.15
MIN_VALUE: float = 0.15
HUE_BUCKETS: int = 24

# "source_lore_color" strings asking for the packaged atlas colors to be kept as-is
NO_RECOLOR_VALUES: tuple[str, ...] = ("", "no", "none", "false", "off", "keep")

# Type alias for a RGBA pixel
Pixel = tuple[int, int, int, int]


# Utility functions
def get_pixels(image: Image.Image) -> list[Pixel]:
	""" Return every pixel of an image as row-major RGBA tuples.

	>>> get_pixels(Image.new("RGBA", (2, 1), (1, 2, 3, 4)))
	[(1, 2, 3, 4), (1, 2, 3, 4)]
	"""
	return list(image.convert("RGBA").getdata())  # pyright: ignore[reportArgumentType, reportUnknownVariableType]


def get_dominant_color(image: Image.Image) -> tuple[int, int, int] | None:
	""" Extract the dominant color of an image, ignoring transparent, gray and dark pixels.

	The remaining pixels are grouped by hue and weighted by ``saturation * value``, so a small vivid
	area wins over a large washed-out one.

	Args:
		image	(Image.Image):	Image to analyze, usually the project ``pack.png``.
	Returns:
		tuple[int, int, int] | None: Average color of the heaviest hue group, or None when the image has no colored pixel.

	Examples:
		>>> get_dominant_color(Image.new("RGBA", (4, 4), (30, 90, 200, 255)))
		(30, 90, 200)
		>>> get_dominant_color(Image.new("RGBA", (4, 4), (128, 128, 128, 255))) is None  # Gray
		True
		>>> get_dominant_color(Image.new("RGBA", (4, 4), (200, 30, 30, 0))) is None  # Transparent
		True
	"""
	weights: dict[int, float] = {}
	sums: dict[int, tuple[float, float, float]] = {}
	for r, g, b, a in get_pixels(image):
		if a < 128:
			continue
		hue, saturation, value = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
		if saturation < MIN_SATURATION or value < MIN_VALUE:
			continue
		bucket: int = int(hue * HUE_BUCKETS) % HUE_BUCKETS
		weight: float = saturation * value
		weights[bucket] = weights.get(bucket, 0.0) + weight
		r_sum, g_sum, b_sum = sums.get(bucket, (0.0, 0.0, 0.0))
		sums[bucket] = (r_sum + r * weight, g_sum + g * weight, b_sum + b * weight)

	if not weights:
		return None
	best: int = max(weights, key=lambda bucket: weights[bucket])
	total: float = weights[best]
	return (round(sums[best][0] / total), round(sums[best][1] / total), round(sums[best][2] / total))


def recolor_image(image: Image.Image, target: tuple[int, int, int]) -> Image.Image:
	""" Recolor an image so that its average opaque pixel becomes ``target``.

	Hues are rotated by a constant offset while saturation and brightness are scaled, so the gradients
	of the source image survive instead of being flattened to a single flat color. Alpha is untouched.

	Args:
		image	(Image.Image):				Image to recolor.
		target	(tuple[int, int, int]):		RGB color the average opaque pixel should end up at.
	Returns:
		Image.Image: A new RGBA image using the target color range.

	Examples:
		>>> single = Image.new("RGBA", (2, 2), (255, 162, 20, 255))
		>>> recolor_image(single, (20, 100, 255)).getpixel((0, 0))  # A single color lands on the target
		(20, 100, 255, 255)
		>>> recolor_image(Image.new("RGBA", (2, 2), (0, 0, 0, 0)), (20, 100, 255)).getpixel((0, 0))
		(0, 0, 0, 0)
	"""
	pixels: list[Pixel] = get_pixels(image)
	counts: Counter[Pixel] = Counter(pixel for pixel in pixels if pixel[3] > 0)
	if not counts:
		return image.convert("RGBA")
	hsv: dict[Pixel, tuple[float, float, float]] = {p: colorsys.rgb_to_hsv(p[0] / 255, p[1] / 255, p[2] / 255) for p in counts}

	# Weighted circular mean of the hue, plain means for saturation and brightness
	hue_x: float = sum(math.cos(hsv[p][0] * math.tau) * n for p, n in counts.items())
	hue_y: float = sum(math.sin(hsv[p][0] * math.tau) * n for p, n in counts.items())
	total: int = sum(counts.values())
	mean_hue: float = (math.atan2(hue_y, hue_x) / math.tau) % 1.0
	mean_saturation: float = sum(hsv[p][1] * n for p, n in counts.items()) / total
	mean_value: float = sum(hsv[p][2] * n for p, n in counts.items()) / total

	# Offsets landing that average pixel exactly on the target color
	target_hue, target_saturation, target_value = colorsys.rgb_to_hsv(target[0] / 255, target[1] / 255, target[2] / 255)
	hue_offset: float = target_hue - mean_hue
	saturation_scale: float = target_saturation / mean_saturation if mean_saturation else 0.0
	value_scale: float = target_value / mean_value if mean_value else 0.0

	# Remap every distinct color once, then rebuild the image in a single pass
	mapping: dict[Pixel, Pixel] = {}
	for pixel, (hue, saturation, value) in hsv.items():
		r, g, b = colorsys.hsv_to_rgb(
			(hue + hue_offset) % 1.0,
			min(1.0, saturation * saturation_scale) if mean_saturation else target_saturation,
			min(1.0, value * value_scale) if mean_value else target_value,
		)
		mapping[pixel] = (round(r * 255), round(g * 255), round(b * 255), pixel[3])

	new_image: Image.Image = Image.new("RGBA", image.size)
	new_image.putdata([mapping.get(pixel, pixel) for pixel in pixels])
	return new_image


def resolve_source_lore_color(logo_path: str | None = None) -> tuple[int, int, int] | None:
	""" Resolve the ``source_lore_color`` configuration into the color the atlas should use.

	Accepted values are ``"auto"`` (derive it from the logo), any color Pillow understands
	(``"#55FFFF"``, ``"gold"``, ``[85, 255, 255]``), or a falsy value / ``"none"`` to keep the packaged
	atlas colors untouched.

	Args:
		logo_path	(str | None):	Path to the logo used by the ``"auto"`` mode.
	Returns:
		tuple[int, int, int] | None: Target color, or None when no recolor should happen.
	"""
	raw: object = Mem.ctx.meta.get("stewbeet", {}).get("source_lore_color", "auto")

	# Explicit sequence of channels
	if isinstance(raw, list | tuple) and len(raw) >= 3:  # pyright: ignore[reportUnknownArgumentType]
		r, g, b = (int(channel) for channel in raw[:3])  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType]
		return (r, g, b)

	# Explicit color string
	if isinstance(raw, str) and raw.lower() not in ("auto", *NO_RECOLOR_VALUES):
		try:
			rgb: tuple[int, ...] = ImageColor.getrgb(raw)
			return (rgb[0], rgb[1], rgb[2])
		except ValueError:
			stp.warning(f"Invalid 'source_lore_color' value {raw!r}, falling back to the logo colors")

	# Recolor explicitly disabled
	if not raw or (isinstance(raw, str) and raw.lower() in NO_RECOLOR_VALUES):
		return None

	# "auto": derive the color from the logo
	if not logo_path:
		return None
	with Image.open(logo_path) as logo:
		return get_dominant_color(logo)

