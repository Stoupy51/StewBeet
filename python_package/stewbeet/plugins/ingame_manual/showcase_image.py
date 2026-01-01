
# Imports
import os

import stouputils as stp
from PIL import Image

from ...core.__memory__ import Mem
from .image_utils import careful_resize
from .shared_import import SharedMemory


# Functions
def calculate_optimal_grid(item_count: int) -> tuple[int, int]:
	""" Calculate optimal grid dimensions for a given number of items to achieve closest to 16:9 ratio

	Args:
        item_count (int): The total number of items to arrange in the grid.
    Returns:
        tuple[int, int]: The optimal number of rows and columns for the grid.
	"""
	if item_count == 0:
		return 0, 0

	best_ratio_diff: float = float('inf')
	best_rows, best_cols = 1, item_count
	target_ratio: float = 16/9

	# Try different configurations
	for rows in range(1, item_count + 1):
		cols: int = (item_count + rows - 1) // rows  # Ceiling division
		if rows * cols >= item_count:
			ratio: float = cols / rows
			ratio_diff: float = abs(ratio - target_ratio)
			if ratio_diff < best_ratio_diff:
				best_ratio_diff = ratio_diff
				best_rows, best_cols = rows, cols

	return best_rows, best_cols

def generate_showcase_images(showcase_mode: int, categories: dict[str, list[str]], simple_case: Image.Image):
	""" Generate showcase images based on the showcase_mode parameter

    Args:
        showcase_mode   (int): Mode for generating showcase images:
            1 - Showcase items in the manual
            2 - Showcase all items, even those not in the manual
            3 - Showcase both manual items and all items
        categories      (dict[str, list]): Dictionary of categories with items.
        simple_case     (Image.Image): Image of a simple case to use as background for items.
	"""
	# Get items for manual (mode 1 or 3)
	if showcase_mode in [1, 3]:
		manual_items: list[str] = []
		for items in categories.values():
			manual_items.extend(items)
		if manual_items:
			stp.run_in_subprocess(
				create_showcase_image, manual_items, "all_manual_items.png", simple_case,
				str(Mem.ctx.output_directory), Mem.ctx.project_id, SharedMemory.cache_path,
				no_join=True
			)

	# Get all items (mode 2 or 3)
	if showcase_mode in [2, 3]:
		all_items: list[str] = list(Mem.definitions.keys())
		if all_items:
			stp.run_in_subprocess(
				create_showcase_image, all_items, "all_items.png", simple_case,
				str(Mem.ctx.output_directory), Mem.ctx.project_id, SharedMemory.cache_path,
				no_join=True
			)

def create_showcase_image(
	items: list[str], filename: str, simple_case: Image.Image, output_dir: str, project_id: str, cache_path: str
) -> None:
	""" Create a showcase image with items arranged in optimal grid for 16:9 ratio

    Args:
        items           (list[str]): List of item IDs to include in the showcase.
        filename        (str): Name of the output image file.
        simple_case     (Image.Image): Image of a simple case to use as background for items.
		output_dir      (str): Directory to save the output image.
		project_id      (str): Project identifier for path construction.
		cache_path      (str): Path to the cache directory for item textures.
	"""
	if not items:
		return

	rows, cols = calculate_optimal_grid(len(items))

	# Big case size (keeps textures sharp)
	case_size: int = 512

	# Pre-resize the case once, keep mode consistent with final image (RGBA)
	resized_case: Image.Image = simple_case.convert("RGBA").resize((case_size, case_size), Image.Resampling.NEAREST)

	# Canvas size
	img_width = cols * case_size
	img_height = rows * case_size

	# Create canvas (transparent background)
	showcase_image = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))

	# Tile the background: paste resized_case for every grid cell once
	# Doing this separately avoids repeated case pastes mixed with item processing.
	for r in range(rows):
		y = r * case_size
		for c in range(cols):
			x = c * case_size
			# use the C-level paste; cheap and fast
			showcase_image.paste(resized_case, (x, y))

	# Cache for textures to avoid reopening/resizing the same file multiple times
	# Keyed by texture_path; stores PIL Image (already resized to target_size, RGBA)
	texture_cache: dict[str, Image.Image] = {}

	# Pre-calc item target size (89% of case)
	target_size = int(case_size * 0.890625)

	# Process and paste items
	for i, item in enumerate(items):
		row = i // cols
		col = i % cols

		x = col * case_size
		y = row * case_size

		texture_path = f"{cache_path}/items/{project_id}/{item}.png"

		# Load (and cache) resized texture
		resized_item = texture_cache.get(texture_path)
		if resized_item is None:
			try:
				# Attempt to open and convert to RGBA immediately.
				# Using "with" ensures file handles are closed promptly.
				with Image.open(texture_path) as img:
					img_rgba = img.convert("RGBA")
					# careful_resize is presumably tuned for preserving pixel art; use it.
					resized_item = careful_resize(img_rgba, target_size)
			except (FileNotFoundError, OSError):
				stp.warning(f"Missing texture at '{texture_path}', using empty texture for showcase")
				# Create an appropriately sized transparent image instead of 1x1 to avoid repeated resizing
				resized_item = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))

			# Store in cache
			texture_cache[texture_path] = resized_item

		# Center item in the case cell
		item_x = x + (case_size - resized_item.size[0]) // 2
		item_y = y + (case_size - resized_item.size[1]) // 2

		# Paste RGBA image using itself as the mask (no split() and no extra mask object)
		showcase_image.paste(resized_item, (item_x, item_y), resized_item)

	# Save to output directory
	os.makedirs(output_dir, exist_ok=True)
	output_path = os.path.join(output_dir, filename)
	showcase_image = showcase_image.convert("RGB")
	showcase_image.save(output_path)

