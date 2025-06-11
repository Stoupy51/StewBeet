
# Imports
from ...core.__memory__ import Mem
from ...core.constants import PULVERIZING
from ...core.ingredients import FURNACES_RECIPES_TYPES
from .book_components import get_item_component
from .other_utils import convert_shapeless_to_shaped, high_res_font_from_craft
from .page_font import generate_page_font
from .shared_import import FONT_FILE, INVISIBLE_ITEM_WIDTH, MICRO_NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT, SharedMemory


# Generate all craft types content
def generate_craft_content(craft: dict, name: str, page_font: str) -> list:
	""" Generate the content for the craft type
	Args:
		craft		(dict):	The craft dictionary, ex: {"type": "crafting_shaped","result_count": 1,"category": "equipment","shape": ["XXX","X X"],"ingredients": {"X": {"components": {"custom_data": {"iyc": {"adamantium": true}}}}}}
		name		(str):	The name of the item, ex: "adamantium_pickaxe"
		page_font	(str):	The font for the page, ex: "\u0002"
	Returns:
		list:	The content of the craft, ex: [{"text": ...}]
	"""  # noqa: E501
	craft_type = craft["type"]
	content: list[dict|str] = [{"text": "", "font": Mem.ctx.project_id + ':' + FONT_FILE, "color": "white"}]	# Make default font for every next component

	# Convert shapeless crafting to shaped crafting
	if craft_type == "crafting_shapeless":
		craft = convert_shapeless_to_shaped(craft)
		craft_type = "crafting_shaped"

	# If high resolution, get proper page font
	if SharedMemory.high_resolution:
		page_font = high_res_font_from_craft(craft)

	# Show up item title and page font
	titled = name.replace("_", " ").title() + "\n"
	content.append({"text": titled, "font": "minecraft:default", "color": "black", "underlined": True})
	content.append(SMALL_NONE_FONT + page_font + "\n")

	# Generate the image for the page
	generate_page_font(name, page_font, craft)

	# Get result component
	result_count = craft.get("result_count", 1)
	if not craft.get("result"):
		result_component = get_item_component(name, count = result_count)
	else:
		result_component = get_item_component(craft["result"], count = result_count)
	if result_component.get("click_event"):
		del result_component["click_event"]	# Remove click_event for result item (as we already are on the page)
	result_component["text"] = MICRO_NONE_FONT + result_component["text"]	# Left adjustment

	# If the craft is shaped
	if craft_type == "crafting_shaped":

		# Convert each ingredients to its text component
		formatted_ingredients: dict[str, dict] = {}
		for k, v in craft["ingredients"].items():
			formatted_ingredients[k] = get_item_component(v)

		# Add each ingredient to the craft
		for line in craft["shape"]:
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
				content.append("\n")
		if len(craft["shape"]) == 1 and len(craft["shape"][0]) < 3:
			content.append("\n")
			pass

		# Add the result to the craft
		if len(craft["shape"]) <= 2 and len(craft["shape"][0]) <= 2:

			# First layer of the square
			len_1 = len(craft["shape"][0])
			offset_1 = 3 - len_1
			break_line_pos = content.index("\n", content.index("\n") + 1)	# Find the second line break
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_1))
			content.insert(break_line_pos + 1, result_component)

			# Second layer of the square
			len_2 = len(craft["shape"][1]) if len(craft["shape"]) > 1 else 0
			offset_2 = 3 - len_2
			if len_2 == 0:
				content.insert(break_line_pos + 2, "\n" + SMALL_NONE_FONT)
			break_line_pos = content.index("\n", break_line_pos + 3)	# Find the third line break
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_2))
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
		else:
			# First layer of the square
			len_line = len(craft["shape"][1]) if len(craft["shape"]) > 1 else 0
			offset = 4 - len_line
			break_line_pos = content.index("\n", content.index("\n") + 1)	# Find the second line break
			try:
				break_line_pos = content.index("\n", break_line_pos + 1) # Find the third line break
			except Exception:
				content.append(SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			content.insert(break_line_pos + 1, result_component)

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

			# Add break lines for the third layer of a 3x3 craft
			if len(craft["shape"]) < 3 and len(craft["shape"][0]) == 3:
				content.append("\n\n")
				if len(craft["shape"]) < 2:
					content.append("\n")


	# If the type is furnace type,
	elif craft_type in FURNACES_RECIPES_TYPES:

		# Convert ingredient to its text component
		formatted_ingredient: dict = get_item_component(craft["ingredient"])

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
			content.append("\n")
		content.append("\n\n")

	# If the type is special Pulverizing,
	elif craft_type == PULVERIZING:

		# Convert ingredient to its text component
		formatted_ingredient: dict = get_item_component(craft["ingredient"])
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
			content.append("\n")
		content.append("\n")
		pass

	return content

