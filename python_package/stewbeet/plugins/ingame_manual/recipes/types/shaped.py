"""Shaped (and shapeless) crafting renderer."""

# ruff: noqa: E501
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from .....core.cls.ingredients import Ingr
from .....core.utils.fonts import save_png
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
from ..grid import append_grid, centred_shape, invisible_copy, place_result_beside
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
		is_small_craft: bool = len(craft["shape"]) <= 2 and all(len(x) <= 2 for x in craft["shape"])
		shape: list[str] = centred_shape(craft["shape"])
		formatted_ingredients: dict[str, JsonDict] = {k: r.item_component(v) for k, v in craft["ingredients"].items()}
		filler: str | None = NONE_FONT * 2 if use_dialog else None
		append_grid(content, shape, formatted_ingredients, filler, columns=2 if is_small_craft else 3, small=is_small_craft)
		if is_small_craft:
			self.place_small_result(content, shape, result_component, use_dialog)
		else:
			place_result_beside(content, shape, result_component, use_dialog, gap_end=SMALL_NONE_FONT * 2, full_width=3)

	@staticmethod
	def place_small_result(content: list[TextComponent], shape: list[str], result_component: JsonDict, use_dialog: bool) -> None:
		""" Put the result of a 2x2 grid right of its rows, on the line of the first row's blank half and the one below. """
		offset_1 = 3 - len(shape[0])
		break_line_pos = content.index("\n", content.index("\n") + 1)
		content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * offset_1))
		content.insert(break_line_pos + 1, result_component)
		if use_dialog:
			content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			break_line_pos += 1

		len_2 = len(shape[1]) if len(shape) > 1 else 0
		if len_2 == 0:
			content.insert(break_line_pos + 2, "\n" + SMALL_NONE_FONT)
		break_line_pos = content.index("\n", break_line_pos + 3)
		content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (3 - len_2)))
		content.insert(break_line_pos + 1, invisible_copy(result_component))
		if use_dialog:
			content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)

	def build_image(self, r: RecipeRenderer, name: str, page_font: str, craft: JsonDict, output_name: str = "") -> None:
		""" Low-resolution PNG of the grid + result pasted onto the shaped template. """
		if r.config.high_resolution:
			return
		output_filename = output_name or name
		result_texture, result_mask = r.images.load_result_texture(name, craft)

		shape: list[str] = centred_shape(craft["shape"])
		shaped_size = max(2, max(len(shape), len(shape[0])))
		template = Image.open(f"{TEMPLATES_PATH}/shaped_{shaped_size}x{shaped_size}.png")
		r.glyphs.add_provider(page_font, f"{r.config.project_id}:font/page/{output_filename}.png", ascent=0 if not output_name else 6, height=60)

		# Each ingredient in its square, 4 pixels from the edge and 4 apart
		cells = ((i, j, symbol) for i, row in enumerate(shape) for j, symbol in enumerate(row) if symbol != " ")
		for i, j, symbol in cells:
			ingredient = Ingr(craft["ingredients"][symbol])
			item: str = (ingredient.to_id() if ingredient.get("components") else ingredient["item"]).replace(":", "/")
			item_texture = r.images.load_square_texture(item)
			template.paste(item_texture, (j * (SQUARE_SIZE + 4) + 4, i * (SQUARE_SIZE + 4) + 4), item_texture.convert("RGBA").split()[3])

		coords = (148, 40) if shaped_size == 3 else (118, 25)
		template.paste(result_texture, coords, result_mask)
		if craft.get("result_count", 1) > 1:
			count_img = r.images.image_count(craft["result_count"])
			template.paste(count_img, [x + 2 for x in coords], count_img)  # pyright: ignore[reportArgumentType]
		save_png(template, f"{r.config.font_cache_path}/page/{output_filename}.png")


register_craft_renderer(ShapedRenderer())

