""" Laying a crafting grid and its result out in a manual page, for the renderers that draw one. """

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ..glyphs import INVISIBLE_ITEM_WIDTH, MICRO_NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT

GRID_END_PAD: str = SMALL_NONE_FONT + VERY_SMALL_NONE_FONT
""" Ends every line of a grid shown without its result, balancing the blank opening them so the dialog centers the grid. """


# Functions
def centred_shape(shape: list[str]) -> list[str]:
	""" A single row or column of three, centred in a 3x3 grid, any other shape as it is.

	>>> centred_shape(["AAA"]), centred_shape(["A", "B", "C"])
	(['   ', 'AAA', '   '], [' A ', ' B ', ' C '])
	"""
	if len(shape) == 1 and len(shape[0]) == 3:
		return ["   ", shape[0], "   "]
	if len(shape) == 3 and all(len(shape_line) == 1 for shape_line in shape):
		return [" " + line + " " for line in shape]
	return shape


def crop_to_grid(template: Image.Image) -> Image.Image:
	""" A crafting template up to the first blank column after its first drawn one, the one separating the grid from the result slot.

	>>> crop_to_grid(Image.new("RGBA", (4, 2))).size
	(4, 2)
	>>> template = Image.new("RGBA", (6, 2))
	>>> template.paste((0, 0, 0, 255), (0, 0, 2, 2))
	>>> template.paste((0, 0, 0, 255), (5, 0, 6, 2))
	>>> crop_to_grid(template).size
	(2, 2)
	>>> template = Image.new("RGBA", (6, 2))
	>>> template.paste((0, 0, 0, 255), (1, 0, 3, 2))
	>>> crop_to_grid(template).size
	(3, 2)
	"""
	alpha = template.getchannel("A")
	drawn: list[bool] = [alpha.crop((x, 0, x + 1, template.height)).getbbox() is not None for x in range(template.width)]
	first = next((x for x, column in enumerate(drawn) if column), None)
	end = template.width if first is None else next((x for x in range(first, template.width) if not drawn[x]), template.width)
	return template.crop((0, 0, end, template.height))


def invisible_copy(component: JsonDict) -> JsonDict:
	""" A copy of a component drawn as blank space, keeping its hover and click. """
	copy: JsonDict = component.copy()
	copy["text"] = INVISIBLE_ITEM_WIDTH
	return copy


def append_grid(
	content: list[TextComponent],
	shape: list[str],
	ingredients: dict[str, JsonDict],
	dialog_filler: str | None,
	columns: int,
	small: bool,
	result_beside: bool = True,
) -> None:
	""" Each row of the grid on two lines, its ingredients then the same components blank, so a cell hovers over its whole height.

	Args:
		dialog_filler: What ends a row in a dialog after padding it to `columns` cells, None outside a dialog, empty for no filler.
		small:         Whether the grid is the small one, whose blank lines a dialog leaves unpadded.
		result_beside: Whether the result is placed right of the rows, which fills the lines a dialog would otherwise pad.
	"""
	for index, line in enumerate(shape):
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			content.extend(grid_cell(symbol, ingredients, i) for symbol in line)
			if dialog_filler is not None and not (result_beside and result_on_line(index, i, small)):
				content.append(INVISIBLE_ITEM_WIDTH * max(0, columns - len(line)))
				if dialog_filler:
					content.append(dialog_filler)
			content.append("\n")
	if len(shape) == 1 and len(shape[0]) < 3:
		content.append("\n")


def result_on_line(row: int, half: int, small: bool) -> bool:
	""" Whether the result is placed on line `half` of grid row `row`: both lines of the middle row, the second only of a small grid.

	>>> [result_on_line(row, half, small=False) for row in range(3) for half in range(2)]
	[False, False, True, True, False, False]
	>>> result_on_line(0, 1, small=True)
	True
	"""
	return row == 1 or (small and half == 1)


def grid_cell(symbol: str, ingredients: dict[str, JsonDict], half: int) -> TextComponent:
	""" A cell on line `half` of its row: blank when empty, else the ingredient on the first line and its blank copy on the second. """
	if symbol == " ":
		return INVISIBLE_ITEM_WIDTH
	return ingredients[symbol] if half == 0 else invisible_copy(ingredients[symbol])


def place_result_beside(
	content: list[TextComponent], shape: list[str], result_component: JsonDict, use_dialog: bool, gap_end: str, full_width: int
) -> None:
	""" Put the result right of the grid's middle row, on both its lines, then pad a grid shorter than three rows of `full_width`.

	Args:
		gap_end: What closes the gap between the middle row and the result, after one blank cell per missing column.
	"""
	len_line: int = len(shape[1]) if len(shape) > 1 else 0
	gap: str = INVISIBLE_ITEM_WIDTH * (4 - len_line - 1) + gap_end
	break_line_pos: int = content.index("\n", content.index("\n") + 1)

	try:
		break_line_pos = content.index("\n", break_line_pos + 1)
	except ValueError:
		content.append(SMALL_NONE_FONT)
		break_line_pos = len(content)
	content.insert(break_line_pos, gap)
	content.insert(break_line_pos + 1, result_component)
	if use_dialog:
		content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
		break_line_pos += 1

	try:
		break_line_pos = content.index("\n", break_line_pos + 3)
	except ValueError:
		content.append("\n" + SMALL_NONE_FONT)
		break_line_pos = len(content)
	content.insert(break_line_pos, gap)
	content.insert(break_line_pos + 1, invisible_copy(result_component))
	if use_dialog:
		content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)

	pad_short_grid(content, shape, full_width)


def pad_short_grid(content: list[TextComponent], shape: list[str], full_width: int) -> None:
	""" Blank lines under a grid of `full_width` columns shorter than three rows, so the buttons below keep their place. """
	if len(shape) < 3 and len(shape[0]) == full_width:
		content.append("\n\n")
		if len(shape) < 2:
			content.append("\n")

