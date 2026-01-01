
# Imports
from beet.core.utils import JsonDict, TextComponent

from ...core.__memory__ import Mem
from ...core.cls.ingredients import FURNACES_RECIPES_TYPES, Ingr
from ...core.utils.text_component import item_id_to_name
from .book_components import get_item_component
from .other_utils import convert_shapeless_to_shaped, high_res_font_from_craft
from .page_font import generate_page_font
from .shared_import import FONT_FILE, INVISIBLE_ITEM_WIDTH, MICRO_NONE_FONT, NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT, SharedMemory


# Generate all craft types content
def generate_craft_content(craft: JsonDict, name: str, page_font: str, in_lore: bool = False) -> list[TextComponent]:
	""" Generate the content for the craft type
	Args:
		craft		(JsonDict):	The craft dictionary, ex: {"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"adamantium": true}}}}}}
		name		(str):	The name of the item, ex: "adamantium_pickaxe"
		page_font	(str):	The font for the page, ex: "\u0002"
	Returns:
		list[TextComponent]:	The content of the craft, ex: [{"text": ...}]
	"""  # noqa: E501
	craft_type = craft["type"]
	content: list[TextComponent] = [{"text": "", "font": Mem.ctx.project_id + ':' + FONT_FILE, "color": "white"}]	# Make default font for every next component

	# Convert shapeless crafting to shaped crafting
	if craft_type == "crafting_shapeless":
		craft = convert_shapeless_to_shaped(craft)
		craft_type = "crafting_shaped"

	# If high resolution, get proper page font
	if SharedMemory.high_resolution:
		page_font = high_res_font_from_craft(craft)
	use_dialog: bool = SharedMemory.use_dialog > 0 and not in_lore	# In lore, we don't need to re-align the content

	# Convert stardust_awakened_forge to shaped crafting
	if craft_type == "stardust_awakened_forge":
		craft = convert_shapeless_to_shaped(craft)
		craft["type"] = "stardust_awakened_forge"

	# Show up item title and page font
	titled = item_id_to_name(name) + "\n"
	content.append({"text": titled, "font": "minecraft:default", "color": "black", "underlined": True})
	padding: str = MICRO_NONE_FONT if use_dialog else ""
	content.append(SMALL_NONE_FONT + padding + page_font + "\n")

	# Generate the image for the page
	generate_page_font(name, page_font, craft)

	# Get result component
	result_count = craft.get("result_count", 1)
	add_change_page_to_ingr: bool = False
	if not craft.get("result"):
		result_component = get_item_component(name, count=result_count, add_change_page=False) # Avoid self-linking page
		add_change_page_to_ingr = True
	else:
		add_change_page_to_ingr = Ingr(craft["result"]).to_id(add_namespace=False) == name
		result_component = get_item_component(craft["result"], count=result_count, add_change_page=not add_change_page_to_ingr)
	result_component["text"] = MICRO_NONE_FONT + result_component["text"]	# Left adjustment

	# If the craft is shaped
	if craft_type == "crafting_shaped":
		shape: list[str] = craft["shape"]
		is_small_craft: bool = len(shape) <= 2 and all(len(x) <= 2 for x in shape)

		# Convert each ingredients to its text component
		formatted_ingredients: dict[str, JsonDict] = {}
		for k, v in craft["ingredients"].items():
			formatted_ingredients[k] = get_item_component(v)

		# Adjust craft shape for special cases
		# Special case: if it's 1 line with 3 columns, add empty lines to center it
		if len(shape) == 1 and len(shape[0]) == 3:
			shape = ["   ", shape[0], "   "]

		# Special case: if it's 3 lines with 1 column each, center them horizontally
		elif (len(shape) == 3 and
			all(len(shape_line) == 1 for shape_line in shape)):
			shape = [" " + line + " " for line in shape]

		# Add each ingredient to the craft
		for index, line in enumerate(shape):
			for i in range(2):	# We need two lines to make a square, otherwise it will be a rectangle
				content.append(SMALL_NONE_FONT)
				for k in line:
					if k == " ":
						content.append(INVISIBLE_ITEM_WIDTH)
					else:
						if i == 0:
							content.append(formatted_ingredients[k])
						else:
							copy = formatted_ingredients[k].copy()
							copy["text"] = INVISIBLE_ITEM_WIDTH
							content.append(copy)
				if use_dialog and index != 1 and (not is_small_craft or i != 1):
					content.append(INVISIBLE_ITEM_WIDTH * max(0, (2 if is_small_craft else 3) - len(line)))
					content.append(NONE_FONT * 2)
				content.append("\n")
		if len(shape) == 1 and len(shape[0]) < 3:
			content.append("\n")
			pass

		# Add the result to the craft
		if is_small_craft:

			# First layer of the square
			len_1 = len(shape[0])
			offset_1 = 3 - len_1
			break_line_pos = content.index("\n", content.index("\n") + 1)	# Find the second line break
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_1))
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1

			# Second layer of the square
			len_2 = len(shape[1]) if len(shape) > 1 else 0
			offset_2 = 3 - len_2
			if len_2 == 0:
				content.insert(break_line_pos + 2, "\n" + SMALL_NONE_FONT)
			break_line_pos = content.index("\n", break_line_pos + 3)	# Find the third line break
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_2))
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
		else:
			# First layer of the square
			len_line = len(shape[1]) if len(shape) > 1 else 0
			offset = 4 - len_line
			break_line_pos = content.index("\n", content.index("\n") + 1)	# Find the second line break
			try:
				break_line_pos = content.index("\n", break_line_pos + 1) # Find the third line break
			except Exception:
				content.append(SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1

			# Second layer of the square
			try:
				break_line_pos = content.index("\n", break_line_pos + 3)	# Find the fourth line break
			except Exception:
				content.append("\n" + SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)

			# Add break lines for the third layer of a 3x3 craft
			if len(shape) < 3 and len(shape[0]) == 3:
				content.append("\n\n")
				if len(shape) < 2:
					content.append("\n")

	# If the craft is stardust_awakened_forge type
	elif craft_type == "stardust_awakened_forge":
		shape: list[str] = craft["shape"]
		is_small_craft: bool = len(shape) <= 3 and all(len(x) <= 3 for x in shape)
		if use_dialog and not is_small_craft:
			content[-1] = content[-1].replace(page_font, page_font + VERY_SMALL_NONE_FONT*2) # type: ignore

		# Convert each ingredients to its text component
		formatted_ingredients: dict[str, JsonDict] = {}
		for k, v in craft["ingredients"].items():
			formatted_ingredients[k] = get_item_component(v, count=v.get("count", 1))

		# Adjust craft shape for special cases
		# Special case: if it's 1 line with 3 columns, add empty lines to center it
		if len(shape) == 1 and len(shape[0]) == 3:
			shape = ["   ", shape[0], "   "]

		# Special case: if it's 3 lines with 1 column each, center them horizontally
		elif (len(shape) == 3 and
			all(len(shape_line) == 1 for shape_line in shape)):
			shape = [" " + line + " " for line in shape]

		# Add each ingredient to the craft
		for index, line in enumerate(shape):
			for i in range(2):	# We need two lines to make a square, otherwise it will be a rectangle
				content.append(SMALL_NONE_FONT)
				for k in line:
					if k == " ":
						content.append(INVISIBLE_ITEM_WIDTH)
					else:
						if i == 0:
							content.append(formatted_ingredients[k])
						else:
							copy = formatted_ingredients[k].copy()
							copy["text"] = INVISIBLE_ITEM_WIDTH
							content.append(copy)
				if use_dialog and index != 1 and (not is_small_craft or i != 1):
					content.append(INVISIBLE_ITEM_WIDTH * max(0, (3 if is_small_craft else 4) - len(line)))
					if is_small_craft:
						content.append(NONE_FONT * 2)
					else:
						content.append(NONE_FONT + SMALL_NONE_FONT)
				content.append("\n")
		if len(shape) == 1 and len(shape[0]) < 3:
			content.append("\n")
			pass

		# Add the result to the craft
		if is_small_craft:
			# First layer of the square
			len_line = len(shape[1]) if len(shape) > 1 else 0
			offset = 4 - len_line
			break_line_pos = content.index("\n", content.index("\n") + 1)	# Find the second line break
			try:
				break_line_pos = content.index("\n", break_line_pos + 1) # Find the third line break
			except Exception:
				content.append(SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1

			# Second layer of the square
			try:
				break_line_pos = content.index("\n", break_line_pos + 3)	# Find the fourth line break
			except Exception:
				content.append("\n" + SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)

			# Add break lines for the third layer of a 3x3 craft
			if len(shape) < 3 and len(shape[0]) == 3:
				content.append("\n\n")
				if len(shape) < 2:
					content.append("\n")
		else:
			# First layer of the square
			len_line = len(shape[1]) if len(shape) > 1 else 0
			offset = 4 - len_line
			break_line_pos = content.index("\n", content.index("\n") + 1)	# Find the second line break
			try:
				break_line_pos = content.index("\n", break_line_pos + 1) # Find the third line break
			except Exception:
				content.append(SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1)) + MICRO_NONE_FONT)
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1

			# Second layer of the square
			try:
				break_line_pos = content.index("\n", break_line_pos + 3)	# Find the fourth line break
			except Exception:
				content.append("\n" + SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1)) + MICRO_NONE_FONT)
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)

			# Add break lines for the third layer of a 3x4 craft
			if len(shape) < 3 and len(shape[0]) == 4:
				content.append("\n\n")
				if len(shape) < 2:
					content.append("\n")
		content.insert(3, "\n")

	# If the type is furnace type,
	elif craft_type in FURNACES_RECIPES_TYPES:

		# Convert ingredient to its text component
		formatted_ingredient: JsonDict = get_item_component(craft["ingredient"], add_change_page=add_change_page_to_ingr)

		# Add the ingredient to the craft
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			if i == 0:
				content.append(formatted_ingredient)
			else:
				copy = formatted_ingredient.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)
			content.append("\n")

		# Add the result to the craft
		for i in range(2):
			content.append(SMALL_NONE_FONT * 4 + INVISIBLE_ITEM_WIDTH * 2)
			if i == 0:
				content.append(result_component)
			else:
				copy = result_component.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)
			if use_dialog:
				content.append(VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			content.append("\n")
		content.append("\n\n")

	# If the type is smithing transform,
	elif craft_type == "smithing_transform":

		# Convert ingredients to their text components
		formatted_base: JsonDict = get_item_component(craft["base"])
		formatted_addition: JsonDict = get_item_component(craft["addition"])
		formatted_template: JsonDict = get_item_component(craft["template"])

		content.append("\n")
		for i in range(2):
			# Add the base item
			content.append(SMALL_NONE_FONT)
			if i == 0:
				content.append(formatted_base)
			else:
				copy = formatted_base.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the template item
			content.append(INVISIBLE_ITEM_WIDTH)
			if i == 0:
				content.append(formatted_template)
			else:
				copy = formatted_template.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the addition item
			content.append(INVISIBLE_ITEM_WIDTH)
			if i == 0:
				content.append(formatted_addition)
			else:
				copy = formatted_addition.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the result
			content.append(SMALL_NONE_FONT + INVISIBLE_ITEM_WIDTH)
			if i == 0:
				content.append(result_component)
			else:
				copy = result_component.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)
			content.append("\n")
		content.append("\n")

	# If the type is smithing trim,
	elif craft_type == "smithing_trim":

		# Convert ingredients to their text components
		formatted_base: JsonDict = get_item_component(craft["base"])
		formatted_addition: JsonDict = get_item_component(craft["addition"])
		formatted_template: JsonDict = get_item_component(craft["template"])
		# Pattern is not an actual item, just use a blank placeholder
		formatted_pattern: JsonDict = {
			"text": INVISIBLE_ITEM_WIDTH,
			"color": "white"
		}

		content.append("\n")
		for i in range(2):
			# Add the base item
			content.append(SMALL_NONE_FONT)
			if i == 0:
				content.append(formatted_base)
			else:
				copy = formatted_base.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the template item
			content.append(INVISIBLE_ITEM_WIDTH)
			if i == 0:
				content.append(formatted_template)
			else:
				copy = formatted_template.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the addition item
			content.append(INVISIBLE_ITEM_WIDTH)
			if i == 0:
				content.append(formatted_addition)
			else:
				copy = formatted_addition.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the pattern placeholder (not an actual item)
			content.append(INVISIBLE_ITEM_WIDTH)
			content.append(formatted_pattern)
			content.append("\n")
		content.append("\n")

	# If the type is special Pulverizing, Stonecutting, or Mining,
	elif craft_type in ("simplenergy_pulverizing", "stonecutting", "mining"):

		# Convert ingredient to its text component
		formatted_ingredient: JsonDict = get_item_component(craft["ingredient"], add_change_page=add_change_page_to_ingr)
		content.append("\n\n")
		for i in range(2):

			# Add the ingredient to the craft
			content.append(SMALL_NONE_FONT)
			if i == 0:
				content.append(formatted_ingredient)
			else:
				copy = formatted_ingredient.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)

			# Add the result to the craft
			content.append(SMALL_NONE_FONT * 4 + VERY_SMALL_NONE_FONT + INVISIBLE_ITEM_WIDTH)
			if i == 0:
				content.append(result_component)
			else:
				copy = result_component.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)
			if use_dialog:
				content.append(VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			content.append("\n")
		content.append("\n")
		pass

	return content

