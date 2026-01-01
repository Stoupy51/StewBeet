
# ruff: noqa: E501
# Imports
import os

import stouputils as stp
from beet.core.utils import JsonDict
from PIL import Image

from ...core.__memory__ import Mem
from ...core.cls.ingredients import FURNACES_RECIPES_TYPES, Ingr
from .image_utils import add_border, careful_resize, image_count
from .shared_import import BORDER_COLOR, BORDER_SIZE, SQUARE_SIZE, TEMPLATES_PATH, WIKI_INGR_OF_CRAFT_FONT, SharedMemory, get_next_font


# Generate page font function (called in utils)
def generate_page_font(name: str, page_font: str, craft: JsonDict|None = None, output_name: str = "") -> None:
	""" Generate the page font image with the proper items
	Args:
		name			(str):			Name of the item
		page_font		(str):			Font string for the page
		craft			(dict|None):	Crafting recipe dictionary (None if no craft)
		output_name		(str|None):		The output name (None if default, used for wiki crafts)
	"""
	# Skip if high resolution and craft is defined
	if SharedMemory.high_resolution and craft is not None:
		return

	# Determine output filename
	if not output_name:
		output_filename = name
	else:
		output_filename = output_name

	# Get result texture (to place later)
	image_path = f"{SharedMemory.cache_path}/items/{Mem.ctx.project_id}/{name}.png"
	if not os.path.exists(image_path):
		stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
		result_texture = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), (255, 255, 255, 0))  # Placeholder image
	else:
		result_texture = Image.open(image_path)

	# If recipe result is specified, take the right texture
	if craft and craft.get("result"):
		result_id = Ingr(craft["result"]).to_id()
		result_id = result_id.replace(":", "/")
		image_path = f"{SharedMemory.cache_path}/items/{result_id}.png"
		if not os.path.exists(image_path):
			stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
			result_texture = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), (255, 255, 255, 0))
		else:
			result_texture = Image.open(image_path)

	# Check if there is a craft and not high resolution
	if craft:

		# Resize the texture and get the mask
		result_texture = careful_resize(result_texture, SQUARE_SIZE)
		result_mask = result_texture.convert("RGBA").split()[3]

		# Shaped craft
		if craft["type"] in "crafting_shaped":
			shape: list[str] = craft["shape"]

			# Adjust craft shape for special cases
			# Special case: if it's 1 line with 3 columns, add empty lines to center it
			if len(shape) == 1 and len(shape[0]) == 3:
				shape = ["   ", shape[0], "   "]

			# Special case: if it's 3 lines with 1 column each, center them horizontally
			elif (len(shape) == 3 and
				all(len(shape_line) == 1 for shape_line in shape)):
				shape = [" " + line + " " for line in shape]

			# Get the image template and append the provider
			shaped_size = max(2, max(len(shape), len(shape[0])))
			template = Image.open(f"{TEMPLATES_PATH}/shaped_{shaped_size}x{shaped_size}.png")
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/{output_filename}.png", "ascent": 0 if not output_name else 6, "height": 60, "chars": [page_font]})

			# Loop the shape matrix
			STARTING_PIXEL = (4, 4)
			CASE_OFFSETS = (4, 4)
			for i, row in enumerate(shape):
				for j, symbol in enumerate(row):
					if symbol != " ":
						ingredient = Ingr(craft["ingredients"][symbol])
						if ingredient.get("components"):
							# get "iyc:steel_ingot" in {'components': {'custom_data': {'iyc': {'steel_ingot': True}}}}
							item = ingredient.to_id()
						else:
							item = ingredient["item"]	# Vanilla item, ex: "minecraft:glowstone"

						# Get the texture and place it at the coords
						item = item.replace(":", "/")
						image_path = f"{SharedMemory.cache_path}/items/{item}.png"
						if not os.path.exists(image_path):
							stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
							item_texture = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), (255, 255, 255, 0))  # Placeholder image
						else:
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
			template.save(f"{SharedMemory.cache_path}/font/page/{output_filename}.png")

		# Smelting craft
		elif craft["type"] in FURNACES_RECIPES_TYPES:

			# Get the image template and append the provider
			template = Image.open(f"{TEMPLATES_PATH}/furnace.png")
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/{output_filename}.png", "ascent": 0 if not output_name else 6, "height": 60, "chars": [page_font]})

			# Place input item
			input_item: str = Ingr(craft["ingredient"]).to_id()
			input_item = input_item.replace(":", "/")
			image_path = f"{SharedMemory.cache_path}/items/{input_item}.png"
			if not os.path.exists(image_path):
				stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
				item_texture = Image.new("RGBA", (SQUARE_SIZE, SQUARE_SIZE), (255, 255, 255, 0))  # Placeholder image
			else:
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
			template.save(f"{SharedMemory.cache_path}/font/page/{output_filename}.png")

	# Else, there is no craft, just put the item in a box
	else:
		# Get the image template and append the provider
		template = Image.open(f"{TEMPLATES_PATH}/simple_case_no_border.png")
		factor: int = 1
		if SharedMemory.high_resolution:
			factor_float: float = 256 / template.size[0]
			result_texture = careful_resize(result_texture, round(SQUARE_SIZE * factor_float))
			template = careful_resize(template, 256)
			result_mask = result_texture.convert("RGBA").split()[3]
			factor = int(factor_float)
		else:
			# Resize the texture and get the mask
			result_texture = careful_resize(result_texture, SQUARE_SIZE)
			result_mask = result_texture.convert("RGBA").split()[3]
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/{output_filename}.png", "ascent": 0 if not output_name else 6, "height": 40, "chars": [page_font]})

		# Place the result item
		template.paste(result_texture, (2 * factor, 2 * factor), result_mask)
		template = add_border(template, BORDER_COLOR, BORDER_SIZE)
		template.save(f"{SharedMemory.cache_path}/font/page/{output_filename}.png")
	return


# Generate small craft icon
def generate_wiki_font_for_ingr(name: str, craft: JsonDict) -> str:
	""" Generate the wiki icon font to display in the manual for wiki buttons showing the result of the craft
	If no texture found for the resulting item, return the default wiki font
	Args:
		name	(str):		The name of the item, ex: "adamantium_fragment"
		craft	(JsonDict):	The associed craft, ex: {"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"adamantium_fragment": true}}}}},"result": {"components": {"custom_data": {"iyc": {"adamantium_helmet": true}}},"count": 1}}
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
		craft_type = craft["type"]
		result_item: str = Ingr(craft["result"]).to_id().replace(":", "/")
		texture_path = f"{SharedMemory.cache_path}/items/{result_item}.png"
		result_item = result_item.replace("/", "_")
		dest_path = f"{SharedMemory.cache_path}/font/wiki_icons/{result_item}_{craft_type}.png"

		# Load texture and resize it
		item_texture = Image.open(texture_path)
		item_res = 64 if not SharedMemory.high_resolution else 256
		item_res_adjusted = int(item_res * 0.75)
		item_texture = careful_resize(item_texture, item_res_adjusted)
		item_texture = item_texture.convert("RGBA")

		# Load the template
		filename: str = "wiki_ingredient_of_craft_template.png" if craft_type != "mining" else "wiki_mining_template.png"
		template = Image.open(f"{TEMPLATES_PATH}/{filename}")
		template = careful_resize(template, item_res)

		# Paste the texture on it
		offset = (item_res - item_res_adjusted) // 2
		template.paste(item_texture, (offset, offset), item_texture)

		# Save the result
		template.save(dest_path)

		# Prepare provider
		font = get_next_font()
		rel_path: str = dest_path.replace(f"{SharedMemory.cache_path}/", f"{Mem.ctx.project_id}:")
		SharedMemory.font_providers.append({"type":"bitmap","file":rel_path, "ascent": 8, "height": 16, "chars": [font]})

	except Exception as e:
		stp.warning(f"Failed to generate craft icon for {name}: {e}\nreturning default font...")
		pass

	# Return the font
	return font

