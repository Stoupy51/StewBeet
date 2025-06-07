
# Imports
import os

import stouputils as stp


# Utils functions for fonts (item start at 0x0000, pages at 0xa000)
# Return the character that will be used for font, ex: chr(0x0002) with i = 2
def get_font(i: int) -> str:
	i += 0x0020	# Minecraft only allow starting this value
	if i > 0xffff:
		stp.error(f"Font index {i} is too big. Maximum is 0xffff.")
	return chr(i)
def get_page_font(i: int) -> str:
	return get_font(i + 0x1000)
def get_next_font() -> str:	# Returns an incrementing value for each craft
	global next_craft_font
	next_craft_font += 1
	return get_font(next_craft_font)


# Constants
COMPONENTS_TO_INCLUDE: list[str] = ["item_name", "lore", "custom_name", "damage", "max_damage"]
SQUARE_SIZE: int = 32
MANUAL_ASSETS_PATH: str = stp.clean_path(os.path.dirname(os.path.realpath(__file__)) + "/")
TEMPLATES_PATH: str = MANUAL_ASSETS_PATH + "templates"
FONT_FILE: str = "manual"
BORDER_COLOR_HEX: int = 0xB64E2F
BORDER_COLOR: tuple[int, int, int, int] = (BORDER_COLOR_HEX >> 16) & 0xFF, (BORDER_COLOR_HEX >> 8) & 0xFF, BORDER_COLOR_HEX & 0xFF, 255
BORDER_SIZE: int = 2
HEAVY_WORKBENCH_CATEGORY: str = "__private_heavy_workbench"
NONE_FONT: str =					get_font(0x0000)
MEDIUM_NONE_FONT: str =				get_font(0x0001)
SMALL_NONE_FONT: str =				get_font(0x0002)
VERY_SMALL_NONE_FONT: str =			get_font(0x0003)
MICRO_NONE_FONT: str =				get_font(0x0004)
WIKI_NONE_FONT: str =				get_font(0x0005)
WIKI_INFO_FONT: str =				get_font(0x0006)
WIKI_RESULT_OF_CRAFT_FONT: str =	get_font(0x0007)
WIKI_INGR_OF_CRAFT_FONT: str =		get_font(0x0008)
SHAPED_2X2_FONT: str =				get_font(0x0009)
SHAPED_3X3_FONT: str =				get_font(0x000A)
FURNACE_FONT: str =					get_font(0x000B)
PULVERIZING_FONT: str =				get_font(0x000C)
HOVER_SHAPED_2X2_FONT: str =		get_font(0x000D)
HOVER_SHAPED_3X3_FONT: str =		get_font(0x000E)
HOVER_FURNACE_FONT: str =			get_font(0x000F)
HOVER_PULVERIZING_FONT: str =		get_font(0x0010)
INVISIBLE_ITEM_FONT: str =			get_font(0x0011)	# Invisible item to place
INVISIBLE_ITEM_WIDTH: str =			INVISIBLE_ITEM_FONT + MICRO_NONE_FONT

HOVER_EQUIVALENTS: dict[str, str] = {
	SHAPED_2X2_FONT: HOVER_SHAPED_2X2_FONT,
	SHAPED_3X3_FONT: HOVER_SHAPED_3X3_FONT,
	FURNACE_FONT: HOVER_FURNACE_FONT,
	PULVERIZING_FONT: HOVER_PULVERIZING_FONT,
}

# Global variables
next_craft_font: int = 0x8000
font_providers: list = []
manual_pages: list = []

# Get page number
def get_page_number(item_id: str) -> int:
	for p in manual_pages:
		if p["name"] == item_id:
			return p["number"]
	return -1

