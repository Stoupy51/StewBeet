
# ruff: noqa: RUF012
# Imports
import stouputils as stp
from stouputils.typing import JsonDict


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
	SharedMemory.next_craft_font += 1
	return get_font(SharedMemory.next_craft_font)


# Constants
SQUARE_SIZE: int = 32
MANUAL_ASSETS_PATH: str = stp.get_root_path(__file__)
TEMPLATES_PATH: str = MANUAL_ASSETS_PATH + "/templates"
FONT_FILE: str = "manual"
BORDER_SIZE: int = 2
HEAVY_WORKBENCH_CATEGORY: str = "__private_heavy_workbench"
NONE_FONT: str =					get_font(0x0000)
MEDIUM_NONE_FONT: str =				get_font(0x0001)
SMALL_NONE_FONT: str =				get_font(0x0002)
VERY_SMALL_NONE_FONT: str =			get_font(0x0003)
MICRO_NONE_FONT: str =				get_font(0x0004)
WIKI_NONE_FONT: str =				get_font(0x0010)
WIKI_INFO_FONT: str =				get_font(0x0011)
WIKI_RESULT_OF_CRAFT_FONT: str =	get_font(0x0012)
WIKI_INGR_OF_CRAFT_FONT: str =		get_font(0x0013)
SHAPED_2X2_FONT: str =				get_font(0x0015)
SHAPED_3X3_FONT: str =				get_font(0x0016)
FURNACE_FONT: str =					get_font(0x0017)
STONECUTTING_FONT: str =			get_font(0x0018)
PULVERIZING_FONT: str =				get_font(0x0019)
MINING_FONT: str =					get_font(0x0020)
AWAKENED_3X3_FONT: str =			get_font(0x0021)
AWAKENED_3X4_FONT: str =			get_font(0x0022)
HOVER_SHAPED_2X2_FONT: str =		get_font(0x0025)
HOVER_SHAPED_3X3_FONT: str =		get_font(0x0026)
HOVER_FURNACE_FONT: str =			get_font(0x0027)
HOVER_STONECUTTING_FONT: str =		get_font(0x0028)
HOVER_PULVERIZING_FONT: str =		get_font(0x0029)
HOVER_MINING_FONT: str =			get_font(0x0030)
HOVER_AWAKENED_3X3_FONT: str =		get_font(0x0031)
HOVER_AWAKENED_3X4_FONT: str =		get_font(0x0032)
INVISIBLE_ITEM_FONT: str =			get_font(0x0035)	# Invisible item to place
INVISIBLE_ITEM_WIDTH: str =			INVISIBLE_ITEM_FONT + MICRO_NONE_FONT
BOOK_FONT: str =					get_font(0x0036)
AWAKENED_FORGE_STRUCT_FONT: tuple[str,str] = (get_font(0x0037), get_font(0x0038))

HOVER_EQUIVALENTS: dict[str, str] = {
	SHAPED_2X2_FONT: HOVER_SHAPED_2X2_FONT,
	SHAPED_3X3_FONT: HOVER_SHAPED_3X3_FONT,
	FURNACE_FONT: HOVER_FURNACE_FONT,
	STONECUTTING_FONT: HOVER_STONECUTTING_FONT,
	PULVERIZING_FONT: HOVER_PULVERIZING_FONT,
	MINING_FONT: HOVER_MINING_FONT,
	AWAKENED_3X3_FONT: HOVER_AWAKENED_3X3_FONT,
	AWAKENED_3X4_FONT: HOVER_AWAKENED_3X4_FONT,
}

DEFAULT_NEXT_CRAFT_FONT: int = 0x8000

# Global variables
class SharedMemory:
	components_to_include: list[str] = ["item_name", "lore", "custom_name", "damage", "max_damage"]
	next_craft_font: int = DEFAULT_NEXT_CRAFT_FONT
	font_providers: list[JsonDict] = []
	manual_pages: list[JsonDict] = []
	cache_path: str = "" # Filled later by ingame_manual/__init__.py
	high_resolution: bool = True # Whether to generate high resolution images for items
	use_dialog: int = 0 # Whether to use the dialog system instead of a book for the manual (0 = no, 1 = yes, 2 = yes and no book)

# Get page number
def get_page_number(item_id: str) -> int:
	for p in SharedMemory.manual_pages:
		if p["name"] == item_id:
			return p["number"]
	return -1

def get_item_from_page(page_number: int) -> str:
	for p in SharedMemory.manual_pages:
		if p["number"] == page_number:
			return p["name"]
	return ""

def lighten_color(color_hex: int, factor: float = 1.42) -> tuple[int, int, int, int]:
	"""
	Lighten a color by multiplying each RGB channel by a factor.

	Args:
		color_hex: The input color as a hexadecimal integer (e.g., 0x803721)
		factor: The lightening factor (default: 1.42)

	Returns:
		A tuple (R, G, B, A) representing the lightened color

	>>> target_color = 0xB64E2F
	>>> target_color = (target_color >> 16 & 0xFF, target_color >> 8 & 0xFF, target_color & 0xFF, 255)
	>>> target_color
	(182, 78, 47, 255)
	>>> lighten_color(0x803721)
	(182, 78, 47, 255)
	>>> lighten_color(0x803721) == target_color
	True
	"""
	r = (color_hex >> 16) & 0xFF
	g = (color_hex >> 8) & 0xFF
	b = color_hex & 0xFF

	# Apply lightening factor and clamp to 255
	r = min(255, round(r * factor))
	g = min(255, round(g * factor))
	b = min(255, round(b * factor))

	return (r, g, b, 255)

@stp.simple_cache
def get_border_color() -> tuple[int, int, int, int]:
	""" Get the border color by loading the template image and lightening the top-right corner pixel. """
	from PIL import Image
	img = Image.open(TEMPLATES_PATH + "/simple_case_no_border.png")

	# Get pixel from top-right corner
	width = img.size[0]
	pixel = img.getpixel((width - 1, 0))

	# Convert RGBA tuple to hex (assuming pixel is RGBA)
	if isinstance(pixel, tuple) and len(pixel) >= 3:
		color_hex = (pixel[0] << 16) | (pixel[1] << 8) | pixel[2]
	else:
		# Fallback to old method if pixel format is unexpected
		color_hex = 0x803721

	return lighten_color(color_hex)

