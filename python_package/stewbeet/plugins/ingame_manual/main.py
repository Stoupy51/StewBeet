
# Imports
import json
import os
import shutil
from pathlib import Path
from typing import Any, cast

import stouputils as stp
from beet import Font, LootTable, Texture
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from stewbeet.core.definitions_helper.completion import add_private_custom_data_for_namespace

from ...core.__memory__ import Mem
from ...core.cls.block import Block, NoSilkTouchDrop, VanillaBlock
from ...core.cls.ingredients import CRAFTING_RECIPES_TYPES, Ingr
from ...core.cls.item import Item
from ...core.cls.recipe import (
	AwakenedForgeRecipe,
	BlastingRecipe,
	CampfireCookingRecipe,
	CraftingShapedRecipe,
	CraftingShapelessRecipe,
	PulverizingRecipe,
	SmeltingRecipe,
	SmithingTransformRecipe,
	SmithingTrimRecipe,
	SmokingRecipe,
	StonecuttingRecipe,
)
from ...core.cls.wiki_button import WikiButton
from ...core.constants import (
	CATEGORY,
	NO_SILK_TOUCH_DROP,
	OFFICIAL_LIBS,
	WIKI_COMPONENT,
)
from ...core.definitions_helper import add_item_name_and_lore_if_missing
from ...core.utils.io import super_merge_dict, write_load_file
from ...core.utils.text_component import item_id_to_name
from ..custom_recipes.vanilla import VanillaRecipeHandler
from ..initialize.source_lore_font import find_pack_png
from ..resource_pack.item_models import AutoModel  # Handle new items models (used for the manual and the heavy workbench)
from .book_components import get_item_component
from .book_optimizer import optimize_element, remove_events
from .craft_content import generate_craft_content
from .dialog import generate_dialogs
from .image_utils import (
	add_border,
	careful_resize,
	generate_high_res_font,
	load_simple_case_no_border,
)
from .iso_renders import generate_all_iso_renders
from .other_utils import (
	convert_shapeless_to_shaped,
	generate_otherside_crafts,
	remove_duplicate_furnace_crafts,
	remove_unknown_crafts,
)
from .page_font import generate_page_font, generate_wiki_font_for_ingr
from .shared_import import (
	AWAKENED_3X3_FONT,
	AWAKENED_3X4_FONT,
	AWAKENED_FORGE_STRUCT_FONT,
	BOOK_FONT,
	BORDER_SIZE,
	FONT_FILE,
	FURNACE_FONT,
	HEAVY_WORKBENCH_CATEGORY,
	HOVER_AWAKENED_3X3_FONT,
	HOVER_AWAKENED_3X4_FONT,
	HOVER_EQUIVALENTS,
	HOVER_FURNACE_FONT,
	HOVER_MINING_FONT,
	HOVER_PULVERIZING_FONT,
	HOVER_SHAPED_2X2_FONT,
	HOVER_SHAPED_3X3_FONT,
	HOVER_STONECUTTING_FONT,
	INVISIBLE_ITEM_FONT,
	MANUAL_ASSETS_PATH,
	MEDIUM_NONE_FONT,
	MICRO_NONE_FONT,
	MINING_FONT,
	NONE_FONT,
	PULVERIZING_FONT,
	SHAPED_2X2_FONT,
	SHAPED_3X3_FONT,
	SMALL_NONE_FONT,
	STONECUTTING_FONT,
	TEMPLATES_PATH,
	VERY_SMALL_NONE_FONT,
	WIKI_INFO_FONT,
	WIKI_INGR_OF_CRAFT_FONT,
	WIKI_NONE_FONT,
	WIKI_RESULT_OF_CRAFT_FONT,
	SharedMemory,
	get_border_color,
	get_next_font,
	get_page_font,
	get_page_number,
)
from .showcase_image import generate_showcase_images
from .stardust_forge import get_stardust_forge_page


# Utility functions
def deepcopy(x: Any) -> Any:
	""" Deep copy using JSON serialization, converting WikiButton objects. """
	return json.loads(json.dumps(stp.convert_to_serializable(x)))

@stp.handle_error(message="An error occurred while generating the in-game manual", error_log=stp.LogLevels.ERROR_TRACEBACK)
def manual_main():
	# Copy everything in the manual assets folder to the templates folder
	with stp.super_open(f"{TEMPLATES_PATH}/.gitignore", "w") as f:
		f.write("*")
	shutil.copytree(MANUAL_ASSETS_PATH + "/assets", TEMPLATES_PATH, dirs_exist_ok = True)

	# Copy the manual_overrides folder to the templates folder
	manual_overrides: str = Mem.ctx.meta.get("stewbeet",{}).get("manual", {}).get("manual_overrides", "")
	if manual_overrides and os.path.exists(manual_overrides):
		shutil.copytree(manual_overrides, TEMPLATES_PATH, dirs_exist_ok = True)
		with stp.super_open(f"{TEMPLATES_PATH}/.gitignore", "w") as f:
			f.write("*") # Ensure the .gitignore file is present to avoid committing manual overrides

	# Launch the routine
	routine()

def routine():
	manual_config: JsonDict = Mem.ctx.meta.get("stewbeet",{}).get("manual", {})
	json_dump_path: str = manual_config.get("json_dump_path", "")
	manual_name: str = manual_config.get("name", "")
	if not manual_name:
		manual_name = f"{Mem.ctx.project_name} Manual"
	if len(manual_name) >= 32:
		stp.error(f"Manual name '{manual_name}' is too long (max 32 characters), Minecraft does not support it. Please change it in the stewbeet config.")

	# If smithed crafter is used, add it to the manual (last page that we will move to the second page)
	if OFFICIAL_LIBS["smithed.crafter"]["is_used"]:
		Mem.ctx.assets[Mem.ctx.project_id].textures["item/heavy_workbench"] = Texture(source_path=f"{TEMPLATES_PATH}/heavy_workbench.png")
		obj = Block(
			id="heavy_workbench",
			vanilla_block=VanillaBlock(id=""),
			manual_category=HEAVY_WORKBENCH_CATEGORY,
			override_model={
				"parent":"minecraft:block/cube",
				"texture_size":[64,32],
				"textures":{"0":f"{Mem.ctx.project_id}:item/heavy_workbench"},
				"elements":[{"from":[0,0,0],"to":[16,16,16],"faces":{"north":{"uv":[4,8,8,16],"texture":"#0"},"east":{"uv":[0,8,4,16],"texture":"#0"},"south":{"uv":[12,8,16,16],"texture":"#0"},"west":{"uv":[8,8,12,16],"texture":"#0"},"up":{"uv":[4,0,8,8],"texture":"#0"},"down":{"uv":[8,0,12,8],"texture":"#0"}}}],
				"display":{"thirdperson_righthand":{"rotation":[75,45,0],"translation":[0,2.5,0],"scale":[0.375,0.375,0.375]},"thirdperson_lefthand":{"rotation":[75,45,0],"translation":[0,2.5,0],"scale":[0.375,0.375,0.375]},"firstperson_righthand":{"rotation":[0,45,0],"scale":[0.4,0.4,0.4]},"firstperson_lefthand":{"rotation":[0,225,0],"scale":[0.4,0.4,0.4]},"ground":{"translation":[0,3,0],"scale":[0.25,0.25,0.25]},"gui":{"rotation":[30,225,0],"scale":[0.625,0.625,0.625]},"head":{"translation":[0,-30.43,0],"scale":[1.601,1.601,1.601]},"fixed":{"scale":[0.5,0.5,0.5]}}
			},
			recipes=[
				CraftingShapedRecipe(shape=["###","#C#","SSS"],ingredients={"#":Ingr("minecraft:oak_log"),"C":Ingr("minecraft:crafting_table"),"S":Ingr("minecraft:smooth_stone")})
			],
			components={
				"item_name": "Heavy Workbench",
				"item_model": f"{Mem.ctx.project_id}:heavy_workbench",
			},
		)
		AutoModel.from_definitions(obj, {}, ignore_textures = True).process()

	# Prework
	os.makedirs(f"{SharedMemory.cache_path}/font/page", exist_ok=True)
	os.makedirs(f"{SharedMemory.cache_path}/font/wiki_icons", exist_ok = True)
	os.makedirs(f"{SharedMemory.cache_path}/font/high_res", exist_ok = True)
	generate_all_iso_renders()

	# Check if there is any awakened forge recipe with 3x3 or 3x4 ingredients
	has_forge_3x3: bool = False
	has_forge_3x4: bool = False
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)
		for recipe in obj.recipes:
			if recipe.get("type") == AwakenedForgeRecipe.type:
				if len(recipe["ingredients"]) <= 9:
					has_forge_3x3 = True
				else:
					has_forge_3x4 = True
		if has_forge_3x3 and has_forge_3x4:
			break

	# Constants
	FONT = Mem.ctx.project_id + ':' + FONT_FILE
	MAX_ITEMS_PER_ROW: int = min(6, manual_config.get("max_items_per_row", 5))
	MAX_ROWS_PER_PAGE: int = min(7, manual_config.get("max_rows_per_page", 5))
	MAX_ITEMS_PER_PAGE = MAX_ITEMS_PER_ROW * MAX_ROWS_PER_PAGE # (for showing up all items in the categories pages)

	# Calculate left padding for categories pages depending on config['max_items_per_row']: higher the value, lower the padding
	LEFT_PADDING = 6 - MAX_ITEMS_PER_ROW
	# Copy assets in the resource pack
	if not manual_config.get("debug_mode", False):
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/none"] = Texture(source_path=f"{TEMPLATES_PATH}/none_release.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/invisible_item"] = Texture(source_path=f"{TEMPLATES_PATH}/invisible_item_release.png")
	else:
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/none"] = Texture(source_path=f"{TEMPLATES_PATH}/none.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/invisible_item"] = Texture(source_path=f"{TEMPLATES_PATH}/invisible_item.png")
	Mem.ctx.assets[Mem.ctx.project_id].textures["font/wiki_information"] = Texture(source_path=f"{TEMPLATES_PATH}/wiki_information.png")
	Mem.ctx.assets[Mem.ctx.project_id].textures["font/wiki_result_of_craft"] = Texture(source_path=f"{TEMPLATES_PATH}/wiki_result_of_craft.png")
	Mem.ctx.assets[Mem.ctx.project_id].textures["font/wiki_ingredient_of_craft"] = Texture(source_path=f"{TEMPLATES_PATH}/wiki_ingredient_of_craft.png")
	if SharedMemory.high_resolution:
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/shaped_2x2"] = Texture(source_path=f"{TEMPLATES_PATH}/shaped_2x2.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/shaped_3x3"] = Texture(source_path=f"{TEMPLATES_PATH}/shaped_3x3.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/furnace"] = Texture(source_path=f"{TEMPLATES_PATH}/furnace.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/stonecutting"] = Texture(source_path=f"{TEMPLATES_PATH}/stonecutting.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/pulverizing"] = Texture(source_path=f"{TEMPLATES_PATH}/pulverizing.png")
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/mining"] = Texture(source_path=f"{TEMPLATES_PATH}/mining.png")
		if has_forge_3x3:
			Mem.ctx.assets[Mem.ctx.project_id].textures["font/awakened_forge_3x3"] = Texture(source_path=f"{TEMPLATES_PATH}/awakened_forge_3x3.png")
		if has_forge_3x4:
			Mem.ctx.assets[Mem.ctx.project_id].textures["font/awakened_forge_3x4"] = Texture(source_path=f"{TEMPLATES_PATH}/awakened_forge_3x4.png")
		if has_forge_3x3 or has_forge_3x4:
			Mem.ctx.assets[Mem.ctx.project_id].textures["font/awakened_forge_1"] = Texture(source_path=f"{TEMPLATES_PATH}/awakened_forge_1.png")
			Mem.ctx.assets[Mem.ctx.project_id].textures["font/awakened_forge_2"] = Texture(source_path=f"{TEMPLATES_PATH}/awakened_forge_2.png")
	if SharedMemory.use_dialog > 0:
		Mem.ctx.assets[Mem.ctx.project_id].textures["font/book"] = Texture(source_path=f"{TEMPLATES_PATH}/book.png")

	# Prepare category padding if dialog
	category_padding: list[str] = [VERY_SMALL_NONE_FONT] if SharedMemory.use_dialog > 0 else []

	# Generate categories list
	categories: dict[str, list[str]] = {}
	for item in Mem.definitions.keys():
		obj = Item.from_id(item)

		if not obj.manual_category:
			stp.suggestion(f"Item '{item}' has no category key. Skipping.")
			continue

		if obj.manual_category not in categories:
			categories[obj.manual_category] = []
		categories[obj.manual_category].append(item)

	# Error message if there is too many categories
	if len(categories) > MAX_ITEMS_PER_PAGE:
		stp.error(f"Too many categories ({len(categories)}). Maximum is {MAX_ITEMS_PER_PAGE}. Please reduce the number of item categories.")

	# Debug categories and sizes
	s = ""
	for file, items in categories.items():
		if file == HEAVY_WORKBENCH_CATEGORY:
			continue
		s += f"\n- {file}: {len(items)} items"
		if len(items) > MAX_ITEMS_PER_PAGE:
			s += f" (splitted into {len(items) // MAX_ITEMS_PER_PAGE + 1} pages)"
	nb_categories: int = len(categories) - (1 if HEAVY_WORKBENCH_CATEGORY in categories else 0)
	stp.debug(f"Found {nb_categories} categories in the definitions:{s}")

	# Split up categories into pages
	categories_pages: dict[str, list[str]] = {}
	for file, items in categories.items():
		if file != HEAVY_WORKBENCH_CATEGORY:
			i = 0
			while i < len(items):
				page_name = file.title()
				if len(items) > MAX_ITEMS_PER_PAGE:
					number = i // MAX_ITEMS_PER_PAGE + 1
					page_name += f" #{number}"
				new_items = items[i:i + MAX_ITEMS_PER_PAGE]
				categories_pages[page_name] = new_items
				i += MAX_ITEMS_PER_PAGE

	# Sort items depending on their category order
	items_with_category = [x for x in [(item, Item.from_id(item)) for item in Mem.definitions.keys()] if x[1].manual_category]
	category_list = list(categories.keys())
	sorted_definitions_on_category = sorted(items_with_category, key = lambda x: category_list.index(x[1].manual_category or ""))

	# If the manual cache is enabled and we have a cache file, load it
	cache_pages: bool = manual_config.get("cache_pages", False)
	if cache_pages and json_dump_path and os.path.exists(json_dump_path) and os.path.exists(f"{SharedMemory.cache_path}/font/manual.json"):
		with stp.super_open(json_dump_path, "r") as f:
			book_content: list[list[TextComponent]] = json.load(f)

		# Make the page dictionary for later use (dialog)
		i: int = 2
		if OFFICIAL_LIBS["smithed.crafter"]["is_used"]:
			SharedMemory.manual_pages.append({"number": i, "name": "heavy_workbench"})
			i += 1
		if has_forge_3x3 or has_forge_3x4:
			SharedMemory.manual_pages.append({"number": i, "name": "stardust_forge"})
			i += 1
		i += 1 # Skip page linking to each category
		for page_name in categories_pages.keys():
			SharedMemory.manual_pages.append({"number": i, "name": page_name})
			i += 1
		for item, _ in sorted_definitions_on_category:
			SharedMemory.manual_pages.append({"number": i, "name": item})
			i += 1
	# Else, generate all
	else:
		## Prepare pages (append categories first, then items depending on categories order)
		i = 2 # Skip first two pages (introduction + categories)

		# Append categories
		for page_name, items in categories_pages.items():
			i += 1
			SharedMemory.manual_pages.append({"number": i, "name": page_name, "raw_data": items, "type": CATEGORY})

		# Append items (sorted by category)
		for item, data in sorted_definitions_on_category:
			i += 1
			SharedMemory.manual_pages.append({"number": i, "name": item, "raw_data": data, "type": "item"})

		# Prepare definitions as Item objects
		definitions_as_objects: dict[str, Item] = {item: Item.from_id(item) for item in Mem.definitions.keys()}

		# Encode pages
		book_content: list[list[TextComponent]] = []
		os.makedirs(f"{SharedMemory.cache_path}/font/category", exist_ok=True)
		simple_case = load_simple_case_no_border(SharedMemory.high_resolution)	# Load the simple case image for later use in categories pages
		def encode_page(page: JsonDict):
			content: list[TextComponent] = []
			number = page["number"]
			raw_data: Item | list[str] = page["raw_data"]
			page_font = ""
			if not SharedMemory.high_resolution:
				page_font = get_page_font(number)
			name = str(page["name"])
			titled = item_id_to_name(name) + "\n"

			# Encode categories {'number': 2, 'name': 'Material #1', 'raw_data': ['adamantium_block', 'adamantium_fragment', ...]}
			if page["type"] == CATEGORY and isinstance(raw_data, list):
				file_name = name.replace(" ", "_").replace("#", "").lower()
				page_font = get_page_font(number)
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/category/{file_name}.png", "ascent": 1, "height": 131, "chars": [page_font]})
				content.append({"text": "", "font": FONT, "color": "white"})	# Make default font for every next component
				content.append({"text": "➤ ", "font": "minecraft:default", "color": "black"})
				content.append({"text": titled, "font": "minecraft:default", "color": "black", "underlined": True})
				content.append(SMALL_NONE_FONT * LEFT_PADDING + page_font + "\n")

				# Prepare image and line list
				page_image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
				x, y = 2, 2	# Prevision for global border and implicit border
				line: list[TextComponent] = []

				# For each item in the category, get its page number and texture, then add it to the image
				max_items_reached: bool = False
				for item in raw_data:

					# Get item texture
					texture_path = f"{SharedMemory.cache_path}/items/{Mem.ctx.project_id}/{item}.png"
					if os.path.exists(texture_path):
						item_image = Image.open(texture_path)
					else:
						stp.warning(f"Missing texture at '{texture_path}', using empty texture")
						item_image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
					if not SharedMemory.high_resolution:
						resized = careful_resize(item_image, 32)
						high_res_font = None
					else:
						resized = Image.new("RGBA", (1, 1), (0, 0, 0, 0))	# Empty texture to use for category page
						high_res_font = generate_high_res_font(item, item_image)

					# Paste the simple case and the item_image
					page_image.paste(simple_case, (x, y))
					mask = resized.convert("RGBA").split()[3]
					page_image.paste(resized, (x + 2, y + 2), mask)
					x += simple_case.size[0]

					# Add the click_event part to the line and add the 2 times the line if enough items
					component = get_item_component(item, only_those_components=[x for x in SharedMemory.components_to_include if x != "lore"])
					component["text"] = MEDIUM_NONE_FONT if not SharedMemory.high_resolution else high_res_font
					line.append(component)
					if len(line) == MAX_ITEMS_PER_ROW:
						max_items_reached = True
						line.insert(0, SMALL_NONE_FONT * LEFT_PADDING)
						content.extend(deepcopy(line))
						content.extend(category_padding)
						for i in range(1, len(line)):
							selected = line[-i]
							if isinstance(selected, dict):
								selected["text"] = MEDIUM_NONE_FONT
						content.extend(["\n", *line, *category_padding, "\n"])
						line = []
						x = 2
						y += simple_case.size[1]

				# If remaining items in the line, add them
				if len(line) > 0:
					if SharedMemory.use_dialog > 0 and max_items_reached:
						line.append(MEDIUM_NONE_FONT * max(0, MAX_ITEMS_PER_ROW - len(line)))
					line.insert(0, SMALL_NONE_FONT * LEFT_PADDING)
					content.extend(deepcopy(line))
					content.extend(category_padding)
					for i in range(1, len(line)):
						selected = line[-i]
						if isinstance(selected, dict):
							selected["text"] = MEDIUM_NONE_FONT
					content.extend(["\n", *line, *category_padding, "\n"])

				# Add the 2 pixels border
				page_image = add_border(page_image, get_border_color(), BORDER_SIZE)

				# Save the image
				page_image.save(f"{SharedMemory.cache_path}/font/category/{file_name}.png")

			# Encode items
			elif isinstance(raw_data, Item):
				# Get all crafts
				crafts: list[JsonDict] = (raw_data.to_dict()["recipes"]).copy()
				crafts += generate_otherside_crafts(name, definitions_as_objects)
				crafts = remove_duplicate_furnace_crafts(crafts, name)
				crafts = remove_unknown_crafts(crafts)
				crafts = stp.unique_list(crafts)

				# Helper function to add count information to mining recipes
				def add_count_to_mining_recipe(mining_recipe: JsonDict, no_silk_drop_data: JsonDict | NoSilkTouchDrop | str | LootTable) -> None:
					if isinstance(no_silk_drop_data, LootTable):
						mining_recipe["dynamic_drop"] = True
						return
					if isinstance(no_silk_drop_data, dict | NoSilkTouchDrop) and "count" in no_silk_drop_data:
						count_data: JsonDict | int = no_silk_drop_data["count"]
						if isinstance(count_data, dict):
							# Range of items like {"min": 2, "max": 8}
							if "min" in count_data and "max" in count_data:
								mining_recipe["result_count"] = f"{count_data['min']}-{count_data['max']}"
							elif "min" in count_data:
								mining_recipe["result_count"] = str(count_data["min"])
							elif "max" in count_data:
								mining_recipe["result_count"] = str(count_data["max"])
						else:
							# Single count value
							mining_recipe["result_count"] = str(count_data)

				# If there is NO_SILK_TOUCH_DROP, add a mining recipe for it
				no_silk_touch_drop: bool = bool(raw_data.get(NO_SILK_TOUCH_DROP, False))
				is_drop_of: list[str] = [
					i for i, d in Mem.definitions.items()
					if d.get(NO_SILK_TOUCH_DROP) and (
						(isinstance(d[NO_SILK_TOUCH_DROP], str) and d[NO_SILK_TOUCH_DROP] == name) or
						(isinstance(d[NO_SILK_TOUCH_DROP], dict | NoSilkTouchDrop) and cast(JsonDict | NoSilkTouchDrop, d[NO_SILK_TOUCH_DROP])["id"] == name)
					)
				]

				# Add mining recipes for items that are drops from other ores
				content_added: bool = False
				if is_drop_of:
					for ore_name in is_drop_of:
						mining_recipe: JsonDict = {
							"type": "mining",
							"ingredient": Ingr(ore_name, Mem.ctx.project_id),  # The ore being mined
							"result": Ingr(name, Mem.ctx.project_id),  # This item is the result
						}
						add_count_to_mining_recipe(mining_recipe, Mem.definitions[ore_name][NO_SILK_TOUCH_DROP])
						crafts.insert(0, mining_recipe)

					# Generate the craft content
					content += generate_craft_content(crafts[0], name, page_font)
					content_added = True

				# Add mining recipe if this item has no_silk_touch_drop (it's an ore)
				if no_silk_touch_drop:
					no_silk_drop_data: JsonDict | NoSilkTouchDrop | str | LootTable = raw_data[NO_SILK_TOUCH_DROP]
					if isinstance(no_silk_drop_data, LootTable):
						mining_recipe = {
							"type": "mining",
							"ingredient": Ingr(name, Mem.ctx.project_id),  # The ore being mined
							"dynamic_drop": True,
						}
					else:
						result_format: str = no_silk_drop_data if isinstance(no_silk_drop_data, str) else no_silk_drop_data["id"]
						mining_recipe = {
							"type": "mining",
							"ingredient": Ingr(name, Mem.ctx.project_id),  # The ore being mined
							"result": Ingr(result_format, Mem.ctx.project_id),  # Proper ingredient format
						}
					add_count_to_mining_recipe(mining_recipe, no_silk_drop_data)

					# Insert at position 0 so it appears first and generate the craft content
					crafts.insert(0, mining_recipe)
					if not content_added:
						content += generate_craft_content(crafts[0], name, page_font)
						content_added = True

				# Else, if there are blue crafts, generate the content for the first craft
				elif not content_added:
					blue_crafts: list[JsonDict] = [craft for craft in crafts if not craft.get("result")]
					if blue_crafts:
						# Sort crafts by result_count in reverse order
						blue_crafts.sort(key=lambda craft: craft.get("result_count", 0), reverse=True)

						# Get the first craft and generate the content
						content += generate_craft_content(blue_crafts[0], name, page_font)
						content_added = True

					# Else, generate the content for the single item in a big box
					else:
						if page_font == "":
							page_font = get_page_font(number)
						generate_page_font(name, page_font, craft = None)
						component = get_item_component(name)
						component["text"] = NONE_FONT
						component["text"] *= 2
						content.append({"text": "", "font": FONT, "color": "white"})	# Make default font for every next component
						content.append({"text": titled, "font": "minecraft:default", "color": "black", "underlined": True})
						if not SharedMemory.use_dialog > 0:
							content.append(MEDIUM_NONE_FONT * 2 + page_font + "\n")
						else:
							content.append(page_font + "\n")

						for _ in range(4):
							if not SharedMemory.use_dialog > 0:
								content.append(MEDIUM_NONE_FONT * 2)
							content.append(component)
							content.append("\n")
						content_added = True

				## Add wiki information if any
				info_buttons: list[JsonDict] = []
				if name == "heavy_workbench":
					content.append([
						{"text":"\nEvery recipe that uses custom items ", "font":"minecraft:default", "color":"black"},
						{"text":"must", "color":"red", "underlined":True},
						{"text":" be crafted using the Heavy Workbench."}
					])
				else:
					if raw_data.get(WIKI_COMPONENT):
						found_event: JsonDict | None = None
						wiki_component: TextComponent | list[WikiButton] = raw_data[WIKI_COMPONENT]
						is_list_of_wiki_button: bool = isinstance(wiki_component, list) and any(isinstance(comp, WikiButton) for comp in wiki_component)
						wiki_buttons: list[TextComponent] = wiki_component if is_list_of_wiki_button else [wiki_component] # type: ignore

						# For each wiki button, add it to the info_buttons list
						for button in wiki_buttons:
							# Convert WikiButton to dict if needed
							if isinstance(button, WikiButton):
								button = button.to_dict()

							# Get click_event if any
							if isinstance(button, dict) and "click_event" in button:
								found_event = button["click_event"]
							elif isinstance(button, list):
								for comp in button:
									if isinstance(comp, dict) and "click_event" in comp:
										found_event = cast(JsonDict, comp["click_event"])
										break

							info_buttons.append({
								"text": WIKI_INFO_FONT + VERY_SMALL_NONE_FONT * 2,
								"hover_event": {
									"action": "show_text",
									"value": button
								}
							})
							if found_event:
								info_buttons[-1]["click_event"] = found_event

					# For each craft (except smelting dupes),
					previous_result: Any = None
					for i, craft in enumerate(crafts):
						if craft["type"] == CraftingShapelessRecipe.type:
							craft = convert_shapeless_to_shaped(craft)

						# Skip if result is same as previous result
						current_result: Any | None = craft.get("result")
						if current_result and current_result == previous_result and craft["type"] != "mining":
							continue
						previous_result = current_result

						# Get breaklines
						breaklines = 3
						if "shape" in craft:
							breaklines = max(2, max(len(craft["shape"]), len(craft["shape"][0])))

						if not SharedMemory.high_resolution:
							craft_font = get_next_font()	# Unique used font for the craft
							generate_page_font(name, craft_font, craft, output_name = f"{name}_{i+1}")
							hover_text: list[TextComponent] = [{"text":""}]
							hover_text.append({"text": craft_font + "\n\n" * breaklines, "font": FONT, "color": "white"})
						else:
							craft_content: list[TextComponent] = generate_craft_content(craft, name, "", in_lore=True)
							craft_content = [craft_content[0], *craft_content[2:]]	# Remove craft title
							remove_events(craft_content)
							for k, v in HOVER_EQUIVALENTS.items():
								if isinstance(craft_content[1], str):
									craft_content[1] = craft_content[1].replace(k, v)
							hover_text = [{"text":""}, craft_content]

						# Add recipe type title
						if craft["type"] not in CRAFTING_RECIPES_TYPES:
							recipe_type_names: dict[str, str] = {
								"mining": "Mining",
								CraftingShapedRecipe.type: "Shaped Recipe",
								CraftingShapelessRecipe.type: "Shapeless Recipe",
								SmeltingRecipe.type: "Smelting",
								BlastingRecipe.type: "Blasting",
								SmokingRecipe.type: "Smoking",
								CampfireCookingRecipe.type: "Campfire Cooking",
								StonecuttingRecipe.type: "Stonecutting",
								SmithingTransformRecipe.type: "Smithing Transform",
								SmithingTrimRecipe.type: "Smithing Trim",
								PulverizingRecipe.type: "(SimplEnergy) Pulverizing",
								AwakenedForgeRecipe.type: "(Stardust Fragment) Awakened Forge",
							}
							recipe_title = recipe_type_names.get(craft["type"], craft["type"].replace("_", " ").title())
							hover_text.append({"text": f"\n{recipe_title}", "color": "yellow"})

						# Append ingredients
						if craft["type"] == "mining":
							# For mining recipes, show what is being mined and what it drops
							ore_name = Ingr(craft["ingredient"]).to_name()
							hover_text.append({"text": "\n- Mine: ", "color": "gray"})
							hover_text.append({"text": ore_name, "color": "gray"})
							if craft.get("dynamic_drop", False):
								hover_text.append({"text": "\n- Drops: variable (loot table)", "color": "gray"})
								hover_text.append({"text": f"\n- Silk touch drop: {ore_name}", "color": "gray"})
							else:
								result_name = Ingr(craft["result"]).to_name()
								result_count = craft.get("result_count", "1")
								hover_text.append({"text": f"\n- Drops: x{result_count} ", "color": "gray"})
								hover_text.append({"text": result_name, "color": "gray"})
						elif craft.get("ingredient"):
							id = Ingr(craft["ingredient"]).to_name()
							hover_text.append({"text": "\n- x1 ", "color": "gray"})
							hover_text.append({"text": id, "color": "gray"})
						elif craft.get("ingredients"):

							# If it's a shaped crafting
							if stp.is_generic_instance(craft["ingredients"], stp.JsonDict):
								for k, v in craft["ingredients"].items():
									id = Ingr(v).to_name()
									count = sum([line.count(k) for line in craft["shape"]])
									hover_text.append({"text": f"\n- x{count} ", "color": "gray"})
									hover_text.append({"text": id, "color": "gray"})

							# If it's shapeless
							elif stp.is_generic_instance(craft["ingredients"], list[stp.JsonDict]):
								ids: dict[str, int] = {}	# {id: count}
								for ingr in craft["ingredients"]:
									id = Ingr(ingr).to_name()
									if id not in ids:
										ids[id] = 0
									ids[id] += ingr.get("count", 1)
								for id, count in ids.items():
									hover_text.append({"text": f"\n- x{count} ", "color": "gray"})
									hover_text.append({"text": id, "color": "gray"})
						else:
							# Smithing crafts
							if craft.get("base"):
								id = Ingr(craft["base"]).to_name()
								hover_text.append({"text": "\n- Base: ", "color": "gray"})
								hover_text.append({"text": id, "color": "gray"})
							if craft.get("template"):
								id = Ingr(craft["template"]).to_name()
								hover_text.append({"text": "\n- Template: ", "color": "gray"})
								hover_text.append({"text": id, "color": "gray"})
							if craft.get("addition"):
								id = Ingr(craft["addition"]).to_name()
								hover_text.append({"text": "\n- Addition: ", "color": "gray"})
								hover_text.append({"text": id, "color": "gray"})
							if craft.get("pattern"):
								pattern_name = str(craft["pattern"]).replace("minecraft:", "").replace("_", " ").title()
								hover_text.append({"text": "\n- Pattern: ", "color": "gray"})
								hover_text.append({"text": pattern_name, "color": "gray"})

						# Add the craft to the content
						result_or_ingredient = WIKI_RESULT_OF_CRAFT_FONT if "result" not in craft else generate_wiki_font_for_ingr(name, craft)
						info_buttons.append({
							"text": result_or_ingredient + VERY_SMALL_NONE_FONT * 2,
							"hover_event": {
								"action": "show_text",
								"value": hover_text
							},
							"priority": craft.get("manual_priority", 1)
						})

						# If there is a result to the craft, try to add the click_event that change to that page
						craft_result: str = "" if "result" not in craft else Ingr(craft["result"]).to_id(add_namespace=False)
						if craft_result and craft_result != name:
							if craft_result in Mem.definitions:
								page_number: int = get_page_number(craft_result)
								if page_number != -1:
									info_buttons[-1]["click_event"] = {
										"action": "change_page",
										"page": page_number,
									}

						# Else, try to add the click_event that change to that page
						else:
							# If there is only one ingredient, link to it
							craft_ingredient: str = ""
							if craft.get("ingredient"):
								craft_ingredient = Ingr(craft["ingredient"]).to_id(add_namespace=False)
							elif craft.get("ingredients") and stp.is_generic_instance(craft["ingredients"], list[stp.JsonDict]) and len(craft["ingredients"]) == 1:
								craft_ingredient = Ingr(craft["ingredients"][0]).to_id(add_namespace=False)
							elif craft.get("ingredients") and stp.is_generic_instance(craft["ingredients"], stp.JsonDict) and len(craft["ingredients"]) == 1:
								craft_ingredient = Ingr(next(iter(craft["ingredients"].values()))).to_id(add_namespace=False)
							if craft_ingredient and craft_ingredient in Mem.definitions and craft_ingredient != name:
								page_number: int = get_page_number(craft_ingredient)
								if page_number != -1:
									info_buttons[-1]["click_event"] = {
										"action": "change_page",
										"page": page_number,
										"blue_craft": craft_result == "" # No result = blue craft
									}

				# Add wiki buttons 5 by 5
				if info_buttons:

					# Retrieve buttons limit depending on number of lines in the content (more lines = less buttons)
					buttons_limit: int = 20 if str(content).count("\\n") <= 6 else 15
					if SharedMemory.use_dialog > 0:
						buttons_limit = 42	# Higher limit

					# If too many buttons, remove all the blue ones (blue_craft) except the last one
					if len(info_buttons) > buttons_limit:
						first_index: int = 0 if not raw_data.get(WIKI_COMPONENT) else 1
						last_index: int = -1
						for i, button in enumerate(info_buttons):
							if button.get("click_event", {}).get("blue_craft", False) and i != first_index:
								last_index = i

						# If there are more than 1 blue button, remove them except the last one
						if (last_index - first_index) > 1:
							info_buttons = info_buttons[:first_index] + info_buttons[last_index:]

						# If there are more than buttons_limit buttons, remove lowest priority ones until there is buttons_limit left
						while len(info_buttons) > buttons_limit:
							lowest_priority: JsonDict = min(info_buttons[::-1], key=lambda x: x.get("priority", 1))
							info_buttons.remove(lowest_priority)

						# Keep only the last buttons_limit buttons (maximum that can be displayed with 5 per line and 4 lines)
						info_buttons = info_buttons[:buttons_limit]

					for button in info_buttons:
						click_event: JsonDict = button.get("click_event", {})
						if click_event.get("blue_craft", False):
							del click_event["blue_craft"]
						if button.get("priority"):
							del button["priority"]

					# Add a breakline only if there aren't too many breaklines already
					content.append("\n")

					last_i = 0
					buttons_per_line = 5 if not SharedMemory.use_dialog > 0 else 6
					for i, button in enumerate(info_buttons):
						last_i = i
						# Duplicate line and add breakline
						if i % buttons_per_line == 0 and i != 0:
							# Remove VERY_SMALL_NONE_FONT from last button to prevent automatic break line
							last_content = cast(JsonDict, content[-1])
							last_content["text"] = last_content["text"].replace(VERY_SMALL_NONE_FONT, "")

							# Re-add last buttons (for good hover_event) but we replace the wiki font by the small font
							content += ["\n"] + [cast(JsonDict, x).copy() for x in content[-buttons_per_line:]]
							for j in range(buttons_per_line):
								selected_content = cast(JsonDict, content[-buttons_per_line + j])
								selected_content["text"] = WIKI_NONE_FONT + VERY_SMALL_NONE_FONT * (2 if j != (buttons_per_line - 1) else 0)
							content.append("\n")
						content.append(button)

					# Duplicate the last line if not done yet
					if last_i % buttons_per_line != 0 or last_i == 0:
						last_i = last_i % buttons_per_line + 1

						# Remove VERY_SMALL_NONE_FONT from last button to prevent automatic break line
						last_content = cast(JsonDict, content[-1])
						last_content["text"] = last_content["text"].replace(VERY_SMALL_NONE_FONT, "")

						content += ["\n"] + [cast(JsonDict, x).copy() for x in content[-last_i:]]
						for j in range(last_i):
							selected_content = cast(JsonDict, content[-last_i + j])
							selected_content["text"] = WIKI_NONE_FONT + VERY_SMALL_NONE_FONT * (2 if j != (last_i - 1) else 0)

			# Add page to the book
			book_content.append(content)
			pass

		# TODO: Make it compatible with multithreading (ordering problem only I think)
		#stp.multithreading(encode_page, SharedMemory.manual_pages, desc="Creating manual pages", max_workers=-1.0)
		for page in stp.colored_for_loop(SharedMemory.manual_pages, desc="Creating manual pages"):
			encode_page(page)

		## Add categories page
		content: list[TextComponent] = []
		file_name = "categories_page"
		page_font = get_page_font(1)
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/category/{file_name}.png", "ascent": 1, "height": 131, "chars": [page_font]})
		content.append({"text": "", "font": FONT, "color": "white"})	# Make default font for every next component
		content.append({"text": "➤ ", "font": "minecraft:default", "color": "black"})
		content.append({"text": "Category browser\n", "font": "minecraft:default", "color": "black", "underlined": True})
		content.append(SMALL_NONE_FONT * LEFT_PADDING + page_font + "\n")

		# Prepare image and line list
		page_image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
		x, y = 2, 2	# Prevision for global border and implicit border
		line: list[TextComponent] = []

		# For each item in the category, get its page number and texture, then add it to the image
		max_items_reached: bool = False
		for page_content in SharedMemory.manual_pages:
			if page_content["type"] == CATEGORY:
				item = page_content["raw_data"][0]

				# Get item texture
				texture_path = f"{SharedMemory.cache_path}/items/{Mem.ctx.project_id}/{item}.png"
				if os.path.exists(texture_path):
					item_image = Image.open(texture_path)
				else:
					stp.warning(f"Missing texture at '{texture_path}', using empty texture")
					item_image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
				if not SharedMemory.high_resolution:
					resized = careful_resize(item_image, 32)
					high_res_font = None
				else:
					resized = Image.new("RGBA", (1, 1), (0, 0, 0, 0))	# Empty texture to use for category page
					high_res_font = generate_high_res_font(item, item_image)

				# Paste the simple case and the item_image
				page_image.paste(simple_case, (x, y))
				mask = resized.convert("RGBA").split()[3]
				page_image.paste(resized, (x + 2, y + 2), mask)
				x += simple_case.size[0]

				# Add the click_event part to the line and add the 2 times the line if enough items
				component = get_item_component(item, ["item_name"])
				component["hover_event"]["components"]["item_name"] = {"text": page_content["name"], "color": "white"}
				component["click_event"]["page"] = page_content["number"]
				if not SharedMemory.high_resolution:
					component["text"] = MEDIUM_NONE_FONT
				else:
					component["text"] = high_res_font
				line.append(component)
				if len(line) == MAX_ITEMS_PER_ROW:
					max_items_reached = True
					line.insert(0, SMALL_NONE_FONT * LEFT_PADDING)
					content += [*deepcopy(line), *category_padding, "\n"]
					for i in range(1, len(line)):
						selected = cast(JsonDict, line[-i])
						selected["text"] = MEDIUM_NONE_FONT
					content += [*line, *category_padding, "\n"]
					line = []
					x = 2
					y += simple_case.size[1]

		# If remaining items in the line, add them
		if len(line) > 0:
			if SharedMemory.use_dialog > 0 and max_items_reached:
				line.append(MEDIUM_NONE_FONT * max(0, MAX_ITEMS_PER_ROW - len(line)))
			line.insert(0, SMALL_NONE_FONT * LEFT_PADDING)
			content += [*deepcopy(line), *category_padding, "\n"]
			for i in range(1, len(line)):
				selected = cast(JsonDict | str, line[-i])
				if isinstance(selected, dict):
					selected["text"] = MEDIUM_NONE_FONT
			content += [*line, *category_padding, "\n"]

		# Add the 2 pixels border
		page_image = add_border(page_image, get_border_color(), BORDER_SIZE)

		# Save the image and add the page to the book
		page_image.save(f"{SharedMemory.cache_path}/font/category/{file_name}.png")
		book_content.insert(0, content)


		## Append introduction page
		intro_content: list[TextComponent] = [{"text":""}]
		page_font = get_page_font(0)
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/page/_logo.png", "ascent": 0, "height": 40, "chars": [page_font]})
		intro_content.append({"text": manual_name + "\n", "underlined": True})
		intro_content.append({"text": MEDIUM_NONE_FONT * (0 if SharedMemory.use_dialog > 0 else 2) + page_font, "font": FONT, "color": "white"})

		# Create the image and load Minecraft font

		icon_path = find_pack_png()
		assert icon_path and os.path.exists(icon_path), "Missing pack.png in your working tree (needed for the manual)"
		logo = Image.open(icon_path)
		logo = careful_resize(logo, 256)

		# Write the introduction text
		intro_content.append({"text": "\n" * 6})
		first_page_config: TextComponent = manual_config.get('first_page_text', "")
		intro_content.append([{"text": "", "font": "minecraft:default", "color": "black"}, first_page_config])

		# Save image and insert in the manual pages
		logo.save(f"{SharedMemory.cache_path}/font/page/_logo.png")
		book_content.insert(0, intro_content)

		## Optimize the book size
		book_content_deepcopy: list[TextComponent] = deepcopy(book_content)	# Deepcopy to avoid sharing same components (such as click_event)
		book_content = cast(list[list[TextComponent]], list(optimize_element(book_content_deepcopy)))

		## Insert at 2nd page the awakened forge
		if has_forge_3x3 or has_forge_3x4:
			book_content.insert(1, get_stardust_forge_page())

			# Increase every change_page click event by 1
			for page_content in book_content:
				for component in page_content:
					if isinstance(component, dict):
						if "click_event" in component and component["click_event"].get("action") == "change_page":
							current_value: int = int(component["click_event"]["page"])
							component["click_event"]["page"] = current_value + 1
			for p in SharedMemory.manual_pages:
				p["number"] += 1

			# Insert heavy workbench page number in the manual pages
			SharedMemory.manual_pages.insert(2, {"number": 2, "name": "awakened_forge", "raw_data": {}, "type": "item"})

		## Insert at 2nd page the heavy workbench
		if "heavy_workbench" in Mem.definitions:
			heavy_workbench_page = book_content.pop(-1)
			book_content.insert(1, heavy_workbench_page)

			# Increase every change_page click event by 1
			for page_content in book_content:
				for component in page_content:
					if isinstance(component, dict):
						if "click_event" in component and component["click_event"].get("action") == "change_page":
							current_value: int = int(component["click_event"]["page"])
							component["click_event"]["page"] = current_value + 1
			for p in SharedMemory.manual_pages:
				p["number"] += 1

			# Insert heavy workbench page number in the manual pages
			SharedMemory.manual_pages.insert(2, {"number": 2, "name": "heavy_workbench", "raw_data": {}, "type": "item"})

		# Add fonts
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/none.png", "ascent": 8, "height": 20, "chars": [NONE_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/none.png", "ascent": 8, "height": 18, "chars": [MEDIUM_NONE_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/none.png", "ascent": 7, "height": 7, "chars": [SMALL_NONE_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/none.png", "ascent": 0, "height": 2, "chars": [VERY_SMALL_NONE_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/none.png", "ascent": 0, "height": 1, "chars": [MICRO_NONE_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/none.png", "ascent": 7, "height": 16, "chars": [WIKI_NONE_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/invisible_item.png", "ascent": 7, "height": 16, "chars": [INVISIBLE_ITEM_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/wiki_information.png", "ascent": 8, "height": 16, "chars": [WIKI_INFO_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/wiki_result_of_craft.png", "ascent": 8, "height": 16, "chars": [WIKI_RESULT_OF_CRAFT_FONT]})
		SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/wiki_ingredient_of_craft.png", "ascent": 8, "height": 16, "chars": [WIKI_INGR_OF_CRAFT_FONT]})
		if SharedMemory.high_resolution:
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/shaped_3x3.png", "ascent": 1, "height": 58, "chars": [SHAPED_3X3_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/shaped_2x2.png", "ascent": 1, "height": 58, "chars": [SHAPED_2X2_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/furnace.png", "ascent": 1, "height": 58, "chars": [FURNACE_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/stonecutting.png", "ascent": 4, "height": 58, "chars": [STONECUTTING_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/pulverizing.png", "ascent": 4, "height": 58, "chars": [PULVERIZING_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/mining.png", "ascent": 4, "height": 58, "chars": [MINING_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/shaped_3x3.png", "ascent": -4, "height": 58, "chars": [HOVER_SHAPED_3X3_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/shaped_2x2.png", "ascent": -2, "height": 58, "chars": [HOVER_SHAPED_2X2_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/furnace.png", "ascent": -3, "height": 58, "chars": [HOVER_FURNACE_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/stonecutting.png", "ascent": -3, "height": 58, "chars": [HOVER_STONECUTTING_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/pulverizing.png", "ascent": -3, "height": 58, "chars": [HOVER_PULVERIZING_FONT]})
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/mining.png", "ascent": -3, "height": 58, "chars": [HOVER_MINING_FONT]})
			if has_forge_3x3:
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/awakened_forge_3x3.png", "ascent": 9, "height": 74, "chars": [AWAKENED_3X3_FONT]})
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/awakened_forge_3x3.png", "ascent": 4, "height": 74, "chars": [HOVER_AWAKENED_3X3_FONT]})
			if has_forge_3x4:
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/awakened_forge_3x4.png", "ascent": 9, "height": 74, "chars": [AWAKENED_3X4_FONT]})
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/awakened_forge_3x4.png", "ascent": 4, "height": 74, "chars": [HOVER_AWAKENED_3X4_FONT]})
			if has_forge_3x3 or has_forge_3x4:
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/awakened_forge_1.png", "ascent": 8, "height": 56, "chars": [AWAKENED_FORGE_STRUCT_FONT[0]]})
				SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/awakened_forge_2.png", "ascent": 8, "height": 56, "chars": [AWAKENED_FORGE_STRUCT_FONT[1]]})
		if SharedMemory.use_dialog > 0:
			SharedMemory.font_providers.append({"type":"bitmap","file":f"{Mem.ctx.project_id}:font/book.png", "ascent": 25, "height": 300, "chars": [BOOK_FONT]})
		fonts = {"providers": SharedMemory.font_providers}
		with stp.super_open(f"{SharedMemory.cache_path}/font/manual.json", "w") as f:
			f.write(stp.json_dump(fonts))

		# Debug book_content
		json_dump_path: str = manual_config.get("json_dump_path", "")
		if json_dump_path:
			with stp.super_open(json_dump_path, "w") as f:
				f.write(stp.json_dump(book_content))
			stp.debug(f"Debug book_content at '{stp.relative_path(json_dump_path)}'")

		# Generate showcase images if requested
		showcase_image: int = manual_config.get("showcase_image", 3)
		if showcase_image > 0:
			generate_showcase_images(showcase_image, categories, simple_case)


	# Copy the font provider and the generated textures to the resource pack
	Mem.ctx.assets[Mem.ctx.project_id].fonts["manual"] = Font(source_path=f"{SharedMemory.cache_path}/font/manual.json")
	for folder in ["category", "page", "wiki_icons", *(["high_res"] if SharedMemory.high_resolution else [])]:
		for file in os.listdir(f"{SharedMemory.cache_path}/font/{folder}"):
			file_path: str = f"{SharedMemory.cache_path}/font/{folder}/{file}"
			no_extension: str = os.path.splitext(file)[0]
			if file.endswith(".png") and os.path.isfile(file_path):
				Mem.ctx.assets[Mem.ctx.project_id].textures[f"font/{folder}/{no_extension}"] = Texture(source_path=file_path)

	# Verify font providers and textures
	for fp in SharedMemory.font_providers:
		if "file" in fp:
			path: str = fp["file"]
			path = os.path.splitext(path.split(":", 1)[-1])[0]  # Remove namespace and extension
			if not Mem.ctx.assets[Mem.ctx.project_id].textures.get(path):
				stp.error(f"Missing font provider at '{path}' for {fp})")
			if len(fp["chars"]) < 1 or (len(fp["chars"]) == 1 and not fp["chars"][0]):
				stp.error(f"Font provider '{path}' has no chars")

	# Generate dialog files if needed
	if SharedMemory.use_dialog > 0:
		generate_dialogs(book_content)

	# Finally, prepend the manual to the definitions if no book, or player still uses it.
	if SharedMemory.use_dialog != 2 or "manual" in Mem.definitions:
		if SharedMemory.use_dialog == 2:
			stp.warning("You beet config says 'use_dialog=2', but a manual item already exists. Please change 'use_dialog' to 1 in stewbeet config.")
		manual_already_exists: bool = "manual" in Mem.definitions
		manual_obj = Item(
			id="manual",
			base_item="minecraft:written_book",
			components={
				"written_book_content": {
					"title": manual_name,
					"author": Mem.ctx.project_author,
					"pages": book_content,
				},
				"item_model": f"{Mem.ctx.project_id}:manual",
				"item_name": manual_name,
				"enchantment_glint_override": False,
				"max_stack_size": 16
			}
		)
		if SharedMemory.use_dialog > 0:
			del manual_obj.components["written_book_content"]
			manual_obj.components["lore"] = [{"text": f"by {Mem.ctx.project_author}", "color": "gray", "italic": False}]
		if manual_already_exists:
			current_def: Item = Item.from_id("manual")
			current_def.components = super_merge_dict(manual_obj.components, current_def.components)
			current_def.base_item = manual_obj.base_item
			Mem.definitions["manual"] = current_def
		add_item_name_and_lore_if_missing(black_list=[item for item in Mem.definitions if item != "manual"])
		add_private_custom_data_for_namespace(black_list=[item for item in Mem.definitions if item != "manual"])

		# Add the model to the resource pack if it doesn't already exist
		if not manual_already_exists:
			textures_folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
			textures: dict[str, str] = {
				stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
				for p in Path(textures_folder).rglob("*.png")
			}
			AutoModel.from_definitions(manual_obj, textures).process()

		# Repair the recipes for the manual
		VanillaRecipeHandler().generate_recipes(override=["manual"])

	# Remove the heavy workbench from the definitions
	if OFFICIAL_LIBS["smithed.crafter"]["is_used"]:
		del Mem.definitions["heavy_workbench"]
		del Mem.ctx.assets[Mem.ctx.project_id].textures["item/heavy_workbench"]
		del Mem.ctx.assets[Mem.ctx.project_id].models["item/heavy_workbench"]
		del Mem.ctx.assets[Mem.ctx.project_id].item_models["heavy_workbench"]

	# Register of the manual in the universal manual
	first_page: str = json.dumps(book_content[0], ensure_ascii=False)
	for r in [("\\n", "\\\\n"), (', "underlined": true','')]:
		first_page = first_page.replace(*r)
	write_load_file(
f"""
# Register the manual to the universal manual
execute unless data storage stewbeet:main universal_manual run data modify storage stewbeet:main universal_manual set value []
data remove storage stewbeet:main universal_manual[{{"name":"{Mem.ctx.project_name}"}}]
data modify storage stewbeet:main universal_manual append value {{"name":"{Mem.ctx.project_name}","loot_table":"{Mem.ctx.project_id}:i/manual","hover":{first_page}}}
""")
	pass

