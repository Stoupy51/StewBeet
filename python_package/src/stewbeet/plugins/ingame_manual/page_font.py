
# ruff: noqa: E501
# Imports
import os

from PIL import Image
from stouputils.print import error, warning

from ...core.__memory__ import Mem
from ...core.ingredients import FURNACES_RECIPES_TYPES, ingr_to_id
from .image_utils import add_border, careful_resize, image_count
from .shared_import import BORDER_COLOR, BORDER_SIZE, SQUARE_SIZE, TEMPLATES_PATH, WIKI_INGR_OF_CRAFT_FONT, SharedMemory, get_next_font


# Generate page font function (called in utils)
def generate_page_font(name: str, page_font: str, craft: dict|None = None, output_name: str = "") -> None:
	""" Generate the page font image with the proper items
	Args:
		name			(str):			Name of the item
		page_font		(str):			Font string for the page
		craft			(dict|None):	Crafting recipe dictionary (None if no craft)
		output_name		(str|None):		The output name (None if default, used for wiki crafts)
	"""
	if not output_name:
		output_filename = name
	else:
		output_filename = output_name

	# Get result texture (to place later)
	image_path = f"{SharedMemory.cache_path}/items/{Mem.ctx.project_id}/{name}.png"
	if not os.path.exists(image_path):
		error(f"Missing item texture at '{image_path}'")
	result_texture = Image.open(image_path)

	# If recipe result is specified, take the right texture
	if craft and craft.get("result"):
		result_id = ingr_to_id(craft["result"])
		result_id = result_id.replace(":", "/")
		image_path = f"{SharedMemory.cache_path}/items/{result_id}.png"
		result_texture = Image.open(image_path)

	# Check if there is a craft
	if craft:

		# Resize the texture and get the mask
		result_texture = careful_resize(result_texture, SQUARE_SIZE)
		result_mask = result_texture.convert("RGBA").split()[3]

		# Shaped craft
		if craft["type"] in "crafting_shaped":

			# Get the image template and append the provider
			shaped_size = max(2, max(len(craft["shape"]), len(craft["shape"][0])))
			template = Image.open(f"{TEMPLATES_PATH}/shaped_{shaped_size}x{shaped_size}.png")
			if not SharedMemory.high_resolution:
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/{output_filename}.png", "ascent": 0 if not output_name else 6, "height": 60, "chars": [page_font]})

			# Loop the shape matrix
			STARTING_PIXEL = (4, 4)
			CASE_OFFSETS = (4, 4)
			for i, row in enumerate(craft["shape"]):
				for j, symbol in enumerate(row):
					if symbol != " ":
						ingredient = craft["ingredients"][symbol]
						if ingredient.get("components"):
							# get "iyc:steel_ingot" in {'components': {'custom_data': {'iyc': {'steel_ingot': True}}}}
							item = ingr_to_id(ingredient)
						else:
							item = ingredient["item"]	# Vanilla item, ex: "minecraft:glowstone"

						# Get the texture and place it at the coords
						item = item.replace(":", "/")
						image_path = f"{SharedMemory.cache_path}/items/{item}.png"
						if not os.path.exists(image_path):
							error(f"Missing item texture at '{image_path}'")
						item_texture = Image.open(image_path)
						item_texture = careful_resize(item_texture, SQUARE_SIZE)
						coords = (
							j * (SQUARE_SIZE + CASE_OFFSETS[0]) + STARTING_PIXEL[0],
							i * (SQUARE_SIZE + CASE_OFFSETS[1]) + STARTING_PIXEL[1]
						)
						mask = item_texture.convert("RGBA").split()[3]
						template.paste(item_texture, coords, mask)

			# Place the result item
			coords = (148, 40) if shaped_size == 3 else (118, 25)
			template.paste(result_texture, coords, result_mask)

			# Place count if the result is greater than 1
			if craft.get("result_count", 1) > 1:
				count_img = image_count(craft["result_count"])
				template.paste(count_img, [x + 2 for x in coords], count_img)	# type: ignore

			# Save the image
			if not SharedMemory.high_resolution:
				template.save(f"{SharedMemory.cache_path}/font/page/{output_filename}.png")

		# Smelting craft
		elif craft["type"] in FURNACES_RECIPES_TYPES:

			# Get the image template and append the provider
			template = Image.open(f"{TEMPLATES_PATH}/furnace.png")
			if not SharedMemory.high_resolution:
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/{output_filename}.png", "ascent": 0 if not output_name else 6, "height": 60, "chars": [page_font]})

			# Place input item
			input_item = ingr_to_id(craft["ingredient"])
			input_item = input_item.replace(":", "/")
			image_path = f"{SharedMemory.cache_path}/items/{input_item}.png"
			if not os.path.exists(image_path):
				error(f"Missing item texture at '{image_path}'")
			item_texture = Image.open(image_path)
			item_texture = careful_resize(item_texture, SQUARE_SIZE)
			mask = item_texture.convert("RGBA").split()[3]
			template.paste(item_texture, (4, 4), mask)

			# Place the result item and count if the result is greater than 1
			coords = (124, 40)
			template.paste(result_texture, coords, result_mask)
			if craft["result_count"] > 1:
				count_img = image_count(craft["result_count"])
				template.paste(count_img, [x + 2 for x in coords], count_img)	# type: ignore

			# Save the image
			if not SharedMemory.high_resolution:
				template.save(f"{SharedMemory.cache_path}/font/page/{output_filename}.png")

	# Else, there is no craft, just put the item in a box
	else:
		# Get the image template and append the provider
		template = Image.open(f"{TEMPLATES_PATH}/simple_case_no_border.png")
		factor = 1
		if SharedMemory.high_resolution:
			factor = 256 // template.size[0]
			result_texture = careful_resize(result_texture, SQUARE_SIZE * factor)
			template = careful_resize(template, 256)
			result_mask = result_texture.convert("RGBA").split()[3]
		else:
			# Resize the texture and get the mask
			result_texture = careful_resize(result_texture, SQUARE_SIZE)
			result_mask = result_texture.convert("RGBA").split()[3]
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/{output_filename}.png", "ascent": 0 if not output_name else 6, "height": 40, "chars": [page_font]})

		# Place the result item
		template.paste(result_texture, (2 * factor, 2 * factor), result_mask)
		template = add_border(template, BORDER_COLOR, BORDER_SIZE, is_rectangle_shape = True)
		template.save(f"{SharedMemory.cache_path}/font/page/{output_filename}.png")
	return


# Generate small craft icon
def generate_wiki_font_for_ingr(name: str, craft: dict) -> str:
	""" Generate the wiki icon font to display in the manual for wiki buttons showing the result of the craft
	If no texture found for the resulting item, return the default wiki font
	Args:
		name	(str):	The name of the item, ex: "adamantium_fragment"
		craft	(dict):	The associed craft, ex: {"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"adamantium_fragment": true}}}}},"result": {"components": {"custom_data": {"iyc": {"adamantium_helmet": true}}},"count": 1}}
	Returns:
		str: The craft icon
	"""
	# Default wiki font
	font = WIKI_INGR_OF_CRAFT_FONT

	# If no result found, return the default font
	if not craft.get("result"):
		return font

	# Get result item texture and paste it on the wiki_ingredient_of_craft_template
	try:
		result_item = ingr_to_id(craft["result"]).replace(":", "/")
		texture_path = f"{SharedMemory.cache_path}/items/{result_item}.png"
		result_item = result_item.replace("/", "_")
		dest_path = f"{SharedMemory.cache_path}/font/wiki_icons/{result_item}.png"

		# Load texture and resize it
		item_texture = Image.open(texture_path)
		item_res = 64 if not SharedMemory.high_resolution else 256
		item_res_adjusted = int(item_res * 0.75)
		item_texture = careful_resize(item_texture, item_res_adjusted)
		item_texture = item_texture.convert("RGBA")

		# Load the template and paste the texture on it
		template = Image.open(f"{TEMPLATES_PATH}/wiki_ingredient_of_craft_template.png")
		template = careful_resize(template, item_res)
		offset = (item_res - item_res_adjusted) // 2
		template.paste(item_texture, (offset, offset), item_texture)

		# Save the result
		template.save(dest_path)

		# Prepare provider
		font = get_next_font()
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/wiki_icons/{result_item}.png", "ascent": 8, "height": 16, "chars": [font]})

	except Exception as e:
		warning(f"Failed to generate craft icon for {name}: {e}\nreturning default font...")
		pass

	# Return the font
	return font

