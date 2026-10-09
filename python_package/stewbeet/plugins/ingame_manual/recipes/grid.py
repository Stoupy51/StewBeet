""" Laying a crafting grid and its result out in a manual page, for the renderers that draw one. """

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ..glyphs import INVISIBLE_ITEM_WIDTH, MICRO_NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT


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
) -> None:
	""" Each row of the grid on two lines, its ingredients then the same components blank, so a cell hovers over its whole height.

	Args:
		dialog_filler: What ends a row in a dialog after padding it to `columns` cells, None outside a dialog.
		small:         Whether the grid is the small one, whose blank lines a dialog leaves unpadded.
	"""
	for index, line in enumerate(shape):
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			content.extend(grid_cell(symbol, ingredients, i) for symbol in line)
			if dialog_filler is not None and index != 1 and (not small or i != 1):
				content.append(INVISIBLE_ITEM_WIDTH * max(0, columns - len(line)))
				content.append(dialog_filler)
			content.append("\n")
	if len(shape) == 1 and len(shape[0]) < 3:
		content.append("\n")


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

	if len(shape) < 3 and len(shape[0]) == full_width:
		content.append("\n\n")
		if len(shape) < 2:
			content.append("\n")

