""" PIL helpers shared by every glyph generator. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import functools
import hashlib
import json
import os
import threading

from PIL import Image, ImageChops, ImageFilter

# Constants
PNG_INDEX_NAME: str = "_png_index.json"
""" File kept next to the pngs `save_png` writes, recording what each of them holds. """

# Variables
png_indexes: dict[str, dict[str, list[str | int]]] = {}
""" Loaded indexes by directory: file name to [pixels digest, size, mtime in ns] of the file `save_png` last wrote. """
dirty_png_indexes: set[str] = set()
""" Directories whose index changed since the last `flush_png_indexes`. """
png_index_lock: threading.Lock = threading.Lock()
""" Guards the two variables above. """


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


def pixels_digest(image: Image.Image) -> str:
	""" A digest of everything Pillow writes in a png: mode, size, palette, info and pixels.

	>>> pixels_digest(Image.new("RGBA", (2, 2), "red")) == pixels_digest(Image.new("RGBA", (2, 2), "red"))
	True
	>>> pixels_digest(Image.new("RGBA", (2, 2), "red")) == pixels_digest(Image.new("RGBA", (2, 2), "blue"))
	False
	"""
	digest = hashlib.sha1(f"{image.mode}|{image.size}|{sorted(image.info.items())!r}".encode())
	palette: list[int] | None = image.getpalette()
	if palette:
		digest.update(bytes(palette))
	digest.update(image.tobytes())
	return digest.hexdigest()


def save_png(image: Image.Image, path: str) -> None:
	""" Save an image as png, unless the file there already holds what `save_png` wrote from the same pixels.

	Encoding is the costly part of generated fonts, and most of them do not change between builds.
	The file's size and modification time are checked too, so a file changed by anything else is written again.
	Call `flush_png_indexes` once the build wrote its images, or the next one encodes them all again.

	>>> import tempfile
	>>> with tempfile.TemporaryDirectory() as tmp:
	...     path = os.path.join(tmp, "red.png")
	...     save_png(Image.new("RGBA", (2, 2), "red"), path)
	...     before = os.stat(path).st_mtime_ns
	...     save_png(Image.new("RGBA", (2, 2), "red"), path)
	...     os.stat(path).st_mtime_ns == before
	True
	"""
	directory, name = os.path.split(os.path.abspath(path))
	digest: str = pixels_digest(image)
	index: dict[str, list[str | int]] = load_png_index(directory)
	current: list[str | int] | None = file_signature(digest, path)
	if current is not None and index.get(name) == current:
		return

	image.save(path)
	signature: list[str | int] | None = file_signature(digest, path)
	with png_index_lock:
		if signature is not None:
			index[name] = signature
		dirty_png_indexes.add(directory)


def source_key(source: str, *parameters: object) -> str | None:
	""" A key for an image drawn from the file at `source` with `parameters`, None when there is no such file.

	The StewBeet version is part of it, since the templates drawn along come with the package.

	>>> source_key("missing.png") is None
	True
	"""
	try:
		stat: os.stat_result = os.stat(source)
	except OSError:
		return None
	described: str = repr((stewbeet_version(), os.path.abspath(source), stat.st_size, stat.st_mtime_ns, parameters))
	return hashlib.sha1(described.encode()).hexdigest()


@functools.cache
def stewbeet_version() -> str:
	""" Installed StewBeet version, or "unknown" when the package metadata is not there. """
	from importlib.metadata import PackageNotFoundError, version
	try:
		return version("stewbeet")
	except PackageNotFoundError:
		return "unknown"


def is_png_recorded(path: str, key: str | None) -> bool:
	""" Whether the png at `path` is the one `record_png` recorded as drawn from `key`, untouched since.

	A generator checks it before even opening its sources, which is what saves the decoding and resizing as well as the encoding.

	>>> import tempfile
	>>> with tempfile.TemporaryDirectory() as tmp:
	...     path = os.path.join(tmp, "red.png")
	...     save_png(Image.new("RGBA", (2, 2), "red"), path)
	...     before = is_png_recorded(path, "key")
	...     record_png(path, "key")
	...     before, is_png_recorded(path, "key"), is_png_recorded(path, "other key")
	(False, True, False)
	"""
	if key is None:
		return False
	directory, name = os.path.split(os.path.abspath(path))
	current: list[str | int] | None = file_signature(key, path)
	return current is not None and load_png_index(directory).get(name) == current


def record_png(path: str, key: str | None) -> None:
	""" Record the png just written at `path` as drawn from `key`, see `is_png_recorded`. """
	if key is None:
		return
	directory, name = os.path.split(os.path.abspath(path))
	index: dict[str, list[str | int]] = load_png_index(directory)
	signature: list[str | int] | None = file_signature(key, path)
	with png_index_lock:
		if signature is not None:
			index[name] = signature
		dirty_png_indexes.add(directory)


def file_signature(digest: str, path: str) -> list[str | int] | None:
	""" The index entry describing the file at `path` as holding `digest`, None when there is no file. """
	try:
		stat: os.stat_result = os.stat(path)
	except OSError:
		return None
	return [digest, stat.st_size, stat.st_mtime_ns]


def load_png_index(directory: str) -> dict[str, list[str | int]]:
	""" The index of a directory, read from disk the first time. """
	with png_index_lock:
		if directory not in png_indexes:
			try:
				with open(os.path.join(directory, PNG_INDEX_NAME), encoding="utf-8") as file:
					png_indexes[directory] = json.load(file)
			except (OSError, ValueError):
				png_indexes[directory] = {}
		return png_indexes[directory]


def flush_png_indexes() -> None:
	""" Write the indexes `save_png` changed, and forget the loaded ones so the next build reads them again. """
	with png_index_lock:
		for directory in dirty_png_indexes:
			if os.path.isdir(directory):
				with open(os.path.join(directory, PNG_INDEX_NAME), "w", encoding="utf-8") as file:
					json.dump(png_indexes.get(directory, {}), file, separators=(",", ":"))
		dirty_png_indexes.clear()
		png_indexes.clear()

