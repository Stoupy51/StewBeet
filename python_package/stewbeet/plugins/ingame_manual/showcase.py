"""Showcase image generation (promotional grids of items).

Ported from v1 ``showcase_image`` with ``renders_path`` passed in rather than read from a global.
"""

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import hashlib
import json
import os

import stouputils as stp
from PIL import Image

from ...core.__memory__ import Mem
from ...core.utils.fonts import careful_resize, pixels_digest

# Constants
SHOWCASE_FORMAT: str = "1"
""" Part of every showcase signature: bump it when `create_showcase_image` draws differently, so existing images are redrawn. """

CACHE_NAME: str = "stewbeet_showcase"
""" Beet cache slot recording what each showcase image on disk was drawn from. """


def calculate_optimal_grid(item_count: int) -> tuple[int, int]:
	""" Grid dimensions closest to a 16:9 aspect ratio for ``item_count`` items.

	>>> calculate_optimal_grid(0)
	(0, 0)
	>>> calculate_optimal_grid(12)
	(3, 4)
	"""
	if item_count == 0:
		return 0, 0
	best_ratio_diff: float = float("inf")
	best_rows, best_cols = 1, item_count
	target_ratio: float = 16 / 9
	for rows in range(1, item_count + 1):
		cols: int = (item_count + rows - 1) // rows
		if rows * cols >= item_count:
			ratio: float = cols / rows
			ratio_diff: float = abs(ratio - target_ratio)
			if ratio_diff < best_ratio_diff:
				best_ratio_diff = ratio_diff
				best_rows, best_cols = rows, cols
	return best_rows, best_cols


def generate_showcase_images(
	showcase_mode: int,
	categories: dict[str, list[str]],
	simple_case: Image.Image,
	renders_path: str,
	all_items: list[str] | None = None,
) -> None:
	""" Generate showcase image(s) per mode (1=manual, 2=all, 3=both).

	When ``all_items`` is given it overrides the default "all items" set (every definition) used for ``all_items.png``: e.g.
	to skip items that have no iso render. Defaults to ``list(Mem.definitions.keys())`` when ``None``.
	"""
	if showcase_mode in (1, 3):
		manual_items: list[str] = []
		for items in categories.values():
			manual_items.extend(items)
		if manual_items:
			start_showcase_image(manual_items, "all_manual_items.png", simple_case, renders_path)
	if showcase_mode in (2, 3):
		if all_items is None:
			all_items = list(Mem.definitions.keys())
		if all_items:
			start_showcase_image(all_items, "all_items.png", simple_case, renders_path)


def start_showcase_image(items: list[str], filename: str, simple_case: Image.Image, renders_path: str) -> None:
	""" Draw one showcase image in a background process, unless the one on disk was drawn from the same inputs.

	Drawing and encoding a grid of every item takes seconds, and the build waits for that process before exiting.
	"""
	output_dir: str = str(Mem.ctx.output_directory)
	signature: str = showcase_signature(items, filename, simple_case, Mem.ctx.project_id, renders_path)
	record_path: str = str(Mem.ctx.cache[CACHE_NAME].directory / f"{filename}.json")
	if is_showcase_up_to_date(os.path.join(output_dir, filename), record_path, signature):
		return
	stp.run_in_subprocess(
		create_showcase_image, items, filename, simple_case, output_dir, Mem.ctx.project_id, renders_path,
		record_path=record_path, signature=signature, no_join=True,
	)


def showcase_signature(items: list[str], filename: str, simple_case: Image.Image, project_id: str, renders_path: str) -> str:
	""" Fingerprint of everything a showcase image is drawn from: the items, their renders on disk and the case template. """
	digest = hashlib.sha1(f"{SHOWCASE_FORMAT}|{filename}|{project_id}|{renders_path}|{pixels_digest(simple_case)}".encode())
	for item in items:
		try:
			stat: os.stat_result = os.stat(f"{renders_path}/{project_id}/{item}.png")
			digest.update(f"|{item}:{stat.st_size}:{stat.st_mtime_ns}".encode())
		except OSError:
			digest.update(f"|{item}:missing".encode())
	return digest.hexdigest()


def is_showcase_up_to_date(image_path: str, record_path: str, signature: str) -> bool:
	""" Whether the image on disk is the one recorded as drawn from `signature`, untouched since. """
	try:
		with open(record_path, encoding="utf-8") as file:
			recorded: list[str | int] = json.load(file)
		stat: os.stat_result = os.stat(image_path)
	except (OSError, ValueError):
		return False
	return recorded == [signature, stat.st_size, stat.st_mtime_ns]


def create_showcase_image(
	items: list[str], filename: str, simple_case: Image.Image, output_dir: str, project_id: str, renders_path: str,
	record_path: str = "", signature: str = "",
) -> None:
	""" Build one composite showcase grid image and save it to ``output_dir``.

	With `record_path`, the image saved is recorded there as drawn from `signature`, see `is_showcase_up_to_date`.
	"""
	if not items:
		return
	rows, cols = calculate_optimal_grid(len(items))
	case_size: int = 512
	resized_case: Image.Image = simple_case.convert("RGBA").resize((case_size, case_size), Image.Resampling.NEAREST)
	img_width = cols * case_size
	img_height = rows * case_size
	showcase_image = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
	for r in range(rows):
		y = r * case_size
		for c in range(cols):
			showcase_image.paste(resized_case, (c * case_size, y))

	texture_cache: dict[str, Image.Image] = {}
	target_size = int(case_size * 0.890625)
	for i, item in enumerate(items):
		row = i // cols
		col = i % cols
		x = col * case_size
		y = row * case_size
		texture_path = f"{renders_path}/{project_id}/{item}.png"
		resized_item = texture_cache.get(texture_path)
		if resized_item is None:
			try:
				with Image.open(texture_path) as img:
					resized_item = careful_resize(img.convert("RGBA"), target_size)
			except (FileNotFoundError, OSError):
				stp.warning(f"Missing texture at '{texture_path}', using empty texture for showcase")
				resized_item = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
			texture_cache[texture_path] = resized_item
		item_x = x + (case_size - resized_item.size[0]) // 2
		item_y = y + (case_size - resized_item.size[1]) // 2
		showcase_image.paste(resized_item, (item_x, item_y), resized_item)

	os.makedirs(output_dir, exist_ok=True)
	image_path: str = os.path.join(output_dir, filename)
	showcase_image.convert("RGB").save(image_path)
	if record_path:
		stat: os.stat_result = os.stat(image_path)
		os.makedirs(os.path.dirname(record_path), exist_ok=True)
		with open(record_path, "w", encoding="utf-8") as file:
			json.dump([signature, stat.st_size, stat.st_mtime_ns], file)

