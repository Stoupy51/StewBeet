
# Imports
import os
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from ...core.__memory__ import Mem
from .shared_import import (
	MICRO_NONE_FONT,
	TEMPLATES_PATH,
	SharedMemory,
	get_next_font,
)


# Generate high res simple case no border
def load_simple_case_no_border(high_res: bool) -> Image.Image:
	path = f"{TEMPLATES_PATH}/simple_case_no_border.png"
	img = Image.open(path)
	if not high_res:
		return img

	# Make the image bigger on the right
	middle_x = img.size[0] // 2
	result = Image.new("RGBA", (img.size[0] + 1, img.size[1]))
	result.paste(img, (0, 0))
	img = img.crop((middle_x, 0, img.size[0], img.size[1]))
	result.paste(img, (middle_x + 1, 0))
	return result


def careful_resize(image: Image.Image, max_result_size: int) -> Image.Image:
	"""Resize an image while keeping the aspect ratio"""
	if image.size[0] >= image.size[1]:
		factor = max_result_size / image.size[0]
		return image.resize((max_result_size, int(image.size[1] * factor)), Image.Resampling.NEAREST)
	else:
		factor = max_result_size / image.size[1]
		return image.resize((int(image.size[0] * factor), max_result_size), Image.Resampling.NEAREST)

def add_border(image: Image.Image, border_color: tuple[int, int, int, int], border_size: int, is_rectangle_shape: bool) -> Image.Image:
	"""Add a border to every part of the image"""
	image = image.convert("RGBA")
	pixels: Any = image.load()

	if not is_rectangle_shape:
		pixels_to_change = [(x, y) for x in range(image.width) for y in range(image.height) if pixels[x, y][3] == 0]
		r = range(-border_size, border_size + 1)
		for x, y in pixels_to_change:
			try:
				if any(pixels[x + dx, y + dy][3] != 0 and pixels[x + dx, y + dy] != border_color for dx in r for dy in r):
					pixels[x, y] = border_color
			except Exception:
				pass
	else:
		height, width = 8, 8
		while height < image.height and pixels[8, height][3]!= 0:
			height += 1
		while width < image.width and pixels[width, 8][3]!= 0:
			width += 1

		border = Image.new("RGBA", (width + 2, height + 2), border_color)
		border.paste(image, (0, 0), image)
		image.paste(border, (0, 0), border)

	return image

# Generate an image showing the result count
def image_count(count: int) -> Image.Image:
	""" Generate an image showing the result count
	Args:
		count (int): The count to show
	Returns:
		Image: The image with the count
	"""
	# Create the image
	img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
	draw = ImageDraw.Draw(img)
	font_size = 16
	font = ImageFont.truetype(f"{TEMPLATES_PATH}/minecraft_font.ttf", size = font_size)

	# Calculate text size and positions of the two texts
	text_width = draw.textlength(str(count), font = font)
	text_height = font_size + 4
	pos_1 = (34-text_width), (32-text_height)
	pos_2 = (32-text_width), (30-text_height)

	# Draw the count
	draw.text(pos_1, str(count), (50, 50, 50), font = font)
	draw.text(pos_2, str(count), (255, 255, 255), font = font)
	return img

# Generate high res image for item
def generate_high_res_font(item: str, item_image: Image.Image, count: int = 1) -> str:
	""" Generate the high res font to display in the manual for the item
	Args:
		item		(str):		The name of the item, ex: "adamantium_fragment"
		item_image	(Image):	The image of the item
		count		(int):		The count of the item
	Returns:
		str: The font to the generated texture
	"""
	font = get_next_font()
	item = f"{item}_{count}" if count > 1 else item

	# Get output path
	path = f"{SharedMemory.cache_path}/font/high_res/{item}.png"
	provider_path = f"{Mem.ctx.project_id}:font/high_res/{item}.png"
	for p in SharedMemory.font_providers:	# Check if it already exists
		if p["file"] == provider_path:
			return MICRO_NONE_FONT + p["chars"][0]
	SharedMemory.font_providers.append({"type":"bitmap","file": provider_path, "ascent": 7, "height": 16, "chars": [font]})


	# Generate high res font
	os.makedirs(os.path.dirname(path), exist_ok = True)
	high_res: int = 256
	resized = careful_resize(item_image, high_res)
	resized = resized.convert("RGBA")

	# Add the item count
	if count > 1:
		img_count = image_count(count)
		img_count = careful_resize(img_count, high_res)
		resized.paste(img_count, (0, 0), img_count)

	# Add invisible pixels for minecraft font at each corner
	total_width = resized.size[0] - 1
	total_height = resized.size[1] - 1
	angles = [(0, 0), (total_width, 0), (0, total_height), (total_width, total_height)]
	for angle in angles:
		resized.putpixel(angle, (0, 0, 0, 100))

	# Save the result and return the font
	resized.save(path)
	return MICRO_NONE_FONT + font

