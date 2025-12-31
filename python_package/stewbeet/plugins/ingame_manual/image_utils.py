
# pyright: reportUnknownMemberType=false
# Imports
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from ...core.__memory__ import JsonDict, Mem
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


def careful_resize(image: Image.Image, max_result_size: int, resampling: Image.Resampling = Image.Resampling.NEAREST) -> Image.Image:
	"""Resize an image while keeping the aspect ratio"""
	if image.size[0] >= image.size[1]:
		factor = max_result_size / image.size[0]
		return image.resize((max_result_size, int(image.size[1] * factor)), resampling)
	else:
		factor = max_result_size / image.size[1]
		return image.resize((int(image.size[0] * factor), max_result_size), resampling)

def ensure_rgba_color(c: tuple[int, ...]) -> tuple[int, int, int, int]:
	""" Ensure the color is in RGBA format """
	if len(c) == 3:
		return (c[0], c[1], c[2], 255)
	if len(c) == 4:
		return c
	raise ValueError("border_color must be (R,G,B) or (R,G,B,A)")

def add_border(
	image: Image.Image,
	border_color: tuple[int, int, int, int],
	border_size: int,
	is_rectangle_shape: bool
) -> Image.Image:
	"""
	Fast border addition using Pillow image filters and compositing.
	- For non-rectangular shapes: dilate the alpha channel and paste border where added.
	- For rectangular shapes: compute bounding box, draw filled rect, dilate, subtract to get border.
	"""
	if border_size <= 0:
		return image

	image = image.convert("RGBA")
	border_color = ensure_rgba_color(border_color)

	# Filter size must be odd; use (2*border_size + 1)
	filt_size = border_size * 2 + 1

	# Work with alpha channel
	alpha = image.split()[3]  # 'L' mode

	if not is_rectangle_shape:
		# Dilate alpha: pixels near opaque become non-zero
		dilated = alpha.filter(ImageFilter.MaxFilter(filt_size))
		# border_mask is where dilated is non-zero but original is zero
		border_mask = ImageChops.difference(dilated, alpha)
	else:
		# Compute bounding box of non-transparent pixels
		bbox = alpha.getbbox()
		if bbox is None:
			# image fully transparent — nothing to border
			return image

		# Create mask with filled rectangle at bbox
		mask = Image.new("L", image.size, 0)
		draw = ImageDraw.Draw(mask)
		draw.rectangle(bbox, fill=255)

		# Dilate the rectangle mask to produce outer rectangle
		dilated = mask.filter(ImageFilter.MaxFilter(filt_size))
		border_mask = ImageChops.difference(dilated, mask)

	# If there's no border (small or fully opaque), return original
	if not border_mask.getbbox():
		return image

	# Create a solid image filled with border_color
	border_layer = Image.new("RGBA", image.size, border_color)

	# Paste the border_layer only where border_mask is non-zero
	out = image.copy()
	out.paste(border_layer, (0, 0), border_mask)
	return out

# Generate an image showing the result count
def image_count(count: int | str) -> Image.Image:
	""" Generate an image showing the result count
	Args:
		count (int | str): The count to show
	Returns:
		Image: The image with the count
	"""
	count = str(count)

	# Create the image
	img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
	draw = ImageDraw.Draw(img)

	# Reduce font size if count is too long
	font_size: int = 16 if len(count) < 3 else 8
	font = ImageFont.truetype(f"{TEMPLATES_PATH}/minecraft_font.ttf", size = font_size)

	# Calculate text size and positions of the two texts
	text_width = draw.textlength(count, font = font)
	text_height = font_size + 4

	# Adjust shadow offset for smaller fonts
	shadow_offset: int = 0 if font_size == 16 else 1
	height_offset: int = 0 if font_size == 16 else 3
	pos_1 = (34-text_width-shadow_offset), (32-text_height-shadow_offset+height_offset)
	pos_2 = (32-text_width), (30-text_height+height_offset)

	# Draw the count
	draw.text(pos_1, count, (50, 50, 50), font = font)
	draw.text(pos_2, count, (255, 255, 255), font = font)
	return img

# Generate high res image for item
def generate_high_res_font(item: str, item_image: Image.Image, count: int | str | JsonDict = 1) -> str:
	""" Generate the high res font to display in the manual for the item
	Args:
		item		(str):		The name of the item, ex: "adamantium_fragment"
		item_image	(Image):	The image of the item
		count		(int):		The count of the item
	Returns:
		str: The font to the generated texture
	"""
	font = get_next_font()
	if isinstance(count, dict):
		count = f"{count.get('min', 1)}-{count.get('max', 1)}"
	item = f"{item}_{str(count).replace('-', '_')}" if isinstance(count, str) or count > 1 else item

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
	if isinstance(count, str) or count > 1:
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

