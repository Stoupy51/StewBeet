"""Showcase image generation (promotional grids of items).

Ported from v1 ``showcase_image`` with ``cache_path`` passed in rather than read from a global.
"""

# Imports
import os

import stouputils as stp
from PIL import Image

from ...core.__memory__ import Mem
from .images import careful_resize


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
	cache_path: str,
	all_items: list[str] | None = None,
) -> None:
	""" Generate showcase image(s) per mode (1=manual, 2=all, 3=both).

	When ``all_items`` is given it overrides the default "all items" set (every definition) used
	for ``all_items.png`` — e.g. to skip items that have no iso render. Defaults to
	``list(Mem.definitions.keys())`` when ``None``.
	"""
	if showcase_mode in (1, 3):
		manual_items: list[str] = []
		for items in categories.values():
			manual_items.extend(items)
		if manual_items:
			stp.run_in_subprocess(
				create_showcase_image, manual_items, "all_manual_items.png", simple_case,
				str(Mem.ctx.output_directory), Mem.ctx.project_id, cache_path, no_join=True,
			)
	if showcase_mode in (2, 3):
		if all_items is None:
			all_items = list(Mem.definitions.keys())
		if all_items:
			stp.run_in_subprocess(
				create_showcase_image, all_items, "all_items.png", simple_case,
				str(Mem.ctx.output_directory), Mem.ctx.project_id, cache_path, no_join=True,
			)


def create_showcase_image(items: list[str], filename: str, simple_case: Image.Image, output_dir: str, project_id: str, cache_path: str) -> None:
	""" Build one composite showcase grid image and save it to ``output_dir``. """
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
		texture_path = f"{cache_path}/items/{project_id}/{item}.png"
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
	showcase_image.convert("RGB").save(os.path.join(output_dir, filename))
