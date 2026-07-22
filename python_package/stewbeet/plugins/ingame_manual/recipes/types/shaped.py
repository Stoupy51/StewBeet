"""Shaped (and shapeless) crafting renderer."""

# ruff: noqa: E501
# Imports
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from .....core.cls.ingredients import Ingr
from ...glyphs import (
	INVISIBLE_ITEM_WIDTH,
	MICRO_NONE_FONT,
	NONE_FONT,
	SHAPED_2X2_FONT,
	SHAPED_3X3_FONT,
	SMALL_NONE_FONT,
	SQUARE_SIZE,
	VERY_SMALL_NONE_FONT,
)
from ...paths import TEMPLATES_PATH
from ..hovers import ingredients_hover
from ..registry import CraftRenderer, register_craft_renderer

if TYPE_CHECKING:
	from ..renderer import RecipeRenderer


@dataclass(slots=True)
class ShapedRenderer(CraftRenderer):
	""" crafting_shaped / crafting_shapeless (shapeless is converted to shaped before rendering). """
	types: ClassVar[tuple[str, ...]] = ("crafting_shaped", "crafting_shapeless")
	name: ClassVar[str] = ""  # crafting recipes show no hover title

	def static_glyph(self, craft: JsonDict) -> str:
		""" 3x3 or 2x2 grid template glyph depending on the craft's shape. """
		return SHAPED_3X3_FONT if (len(craft["shape"]) == 3 or len(craft["shape"][0]) == 3) else SHAPED_2X2_FONT

	def append_hover(self, r: RecipeRenderer, craft: JsonDict, hover: list[TextComponent]) -> None:
		""" Count + list every grid ingredient. """
		ingredients_hover(craft, hover)

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		""" Lay the ingredient grid out over the crafting-table template, then place the result. """
		shape: list[str] = craft["shape"]
		is_small_craft: bool = len(shape) <= 2 and all(len(x) <= 2 for x in shape)
		formatted_ingredients: dict[str, JsonDict] = {k: r.item_component(v) for k, v in craft["ingredients"].items()}

		if len(shape) == 1 and len(shape[0]) == 3:
			shape = ["   ", shape[0], "   "]
		elif len(shape) == 3 and all(len(shape_line) == 1 for shape_line in shape):
			shape = [" " + line + " " for line in shape]

		for index, line in enumerate(shape):
			for i in range(2):
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

		if is_small_craft:
			len_1 = len(shape[0])
			offset_1 = 3 - len_1
			break_line_pos = content.index("\n", content.index("\n") + 1)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_1))
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1
			len_2 = len(shape[1]) if len(shape) > 1 else 0
			offset_2 = 3 - len_2
			if len_2 == 0:
				content.insert(break_line_pos + 2, "\n" + SMALL_NONE_FONT)
			break_line_pos = content.index("\n", break_line_pos + 3)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_2))
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
		else:
			len_line = len(shape[1]) if len(shape) > 1 else 0
			offset = 4 - len_line
			break_line_pos = content.index("\n", content.index("\n") + 1)
			try:
				break_line_pos = content.index("\n", break_line_pos + 1)
			except Exception:
				content.append(SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1
			try:
				break_line_pos = content.index("\n", break_line_pos + 3)
			except Exception:
				content.append("\n" + SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1) + SMALL_NONE_FONT * 2))
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			if len(shape) < 3 and len(shape[0]) == 3:
				content.append("\n\n")
				if len(shape) < 2:
					content.append("\n")

	def build_image(self, r: RecipeRenderer, name: str, page_font: str, craft: JsonDict, output_name: str = "") -> None:
		""" Low-resolution PNG of the grid + result pasted onto the shaped template. """
		if r.config.high_resolution:
			return
		output_filename = output_name or name
		result_texture, result_mask = r.images.load_result_texture(name, craft)

		shape: list[str] = craft["shape"]
		if len(shape) == 1 and len(shape[0]) == 3:
			shape = ["   ", shape[0], "   "]
		elif len(shape) == 3 and all(len(shape_line) == 1 for shape_line in shape):
			shape = [" " + line + " " for line in shape]

		shaped_size = max(2, max(len(shape), len(shape[0])))
		template = Image.open(f"{TEMPLATES_PATH}/shaped_{shaped_size}x{shaped_size}.png")
		r.glyphs.add_provider(page_font, f"{r.config.project_id}:font/page/{output_filename}.png", ascent=0 if not output_name else 6, height=60)

		STARTING_PIXEL = (4, 4)
		CASE_OFFSETS = (4, 4)
		for i, row in enumerate(shape):
			for j, symbol in enumerate(row):
				if symbol != " ":
					ingredient = Ingr(craft["ingredients"][symbol])
					item = ingredient.to_id() if ingredient.get("components") else ingredient["item"]
					item = item.replace(":", "/")
					item_texture = r.images.load_square_texture(item)
					coords = (
						j * (SQUARE_SIZE + CASE_OFFSETS[0]) + STARTING_PIXEL[0],
						i * (SQUARE_SIZE + CASE_OFFSETS[1]) + STARTING_PIXEL[1],
					)
					template.paste(item_texture, coords, item_texture.convert("RGBA").split()[3])

		coords = (148, 40) if shaped_size == 3 else (118, 25)
		template.paste(result_texture, coords, result_mask)
		if craft.get("result_count", 1) > 1:
			count_img = r.images.image_count(craft["result_count"])
			template.paste(count_img, [x + 2 for x in coords], count_img)  # type: ignore
		template.save(f"{r.config.cache_path}/font/page/{output_filename}.png")


register_craft_renderer(ShapedRenderer())
