
# Imports
import os

from PIL import Image
from stouputils.io import relative_path
from stouputils.print import debug, warning

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

def generate_showcase_images(showcase_mode: int, categories: dict[str, list], simple_case: Image.Image):
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
			create_showcase_image(manual_items, "all_manual_items.jpg", simple_case)

	# Get all items (mode 2 or 3)
	if showcase_mode in [2, 3]:
		all_items: list[str] = list(Mem.definitions.keys())
		if all_items:
			create_showcase_image(all_items, "all_items.jpg", simple_case)

def create_showcase_image(items: list[str], filename: str, simple_case: Image.Image):
	""" Create a showcase image with items arranged in optimal grid for 16:9 ratio

    Args:
        items           (list[str]): List of item IDs to include in the showcase.
        filename        (str): Name of the output image file.
        simple_case     (Image.Image): Image of a simple case to use as background for items.
	"""
	if not items:
		return

	rows, cols = calculate_optimal_grid(len(items))

	# Big case size to make sure textures are not distorted
	case_size: int = 512

	# Resize the simple case to match our calculated case size
	resized_case: Image.Image = simple_case.resize((case_size, case_size), Image.Resampling.NEAREST)

	# Calculate image dimensions with border
	img_width: int = cols * case_size
	img_height: int = rows * case_size

	# Create image
	showcase_image: Image.Image = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))

	# Place items
	for i, item in enumerate(items):
		row: int = i // cols
		col: int = i % cols

		x: int = col * case_size
		y: int = row * case_size

		# Get item texture
		texture_path: str = f"{SharedMemory.cache_path}/items/{Mem.ctx.project_id}/{item}.png"
		if os.path.exists(texture_path):
			item_image: Image.Image = Image.open(texture_path)
		else:
			warning(f"Missing texture at '{texture_path}', using empty texture for showcase")
			item_image: Image.Image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))

		# Resize item image to 89% of case size
		target_size: int = int(case_size * (0.890625))
		resized_item: Image.Image = careful_resize(item_image, target_size)

		# Center the resized item image within the case
		item_x: int = x + (case_size - resized_item.size[0]) // 2
		item_y: int = y + (case_size - resized_item.size[1]) // 2

		# Paste the resized case and the item image
		showcase_image.paste(resized_case, (x, y))
		if resized_item.mode == "RGBA":
			mask: Image.Image = resized_item.split()[3]
			showcase_image.paste(resized_item, (item_x, item_y), mask)
		else:
			showcase_image.paste(resized_item, (item_x, item_y))

	# Save to output directory
	os.makedirs(Mem.ctx.output_directory, exist_ok=True)
	output_path = os.path.join(Mem.ctx.output_directory, filename)
	showcase_image.save(output_path, "PNG")
	debug(f"Generated showcase image: {relative_path(output_path)} ({rows}x{cols} grid, {len(items)} items)")

