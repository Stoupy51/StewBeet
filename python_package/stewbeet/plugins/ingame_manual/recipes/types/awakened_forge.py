"""Stardust Fragment Awakened Forge renderer (3x3 / 3x4 grid)."""

# ruff: noqa: E501
# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from .....core.cls.recipe import AwakenedForgeRecipe
from ...glyphs import (
	AWAKENED_3X3_FONT,
	AWAKENED_3X4_FONT,
	INVISIBLE_ITEM_WIDTH,
	MICRO_NONE_FONT,
	NONE_FONT,
	SMALL_NONE_FONT,
	VERY_SMALL_NONE_FONT,
)
from ..hovers import ingredients_hover
from ..registry import CraftRenderer, register_craft_renderer

if TYPE_CHECKING:
	from ..renderer import RecipeRenderer


@dataclass(slots=True)
class AwakenedForgeRenderer(CraftRenderer):
	""" Stardust Fragment ``stardust_awakened_forge`` recipes (3x3 or 3x4 grid). """
	types: ClassVar[tuple[str, ...]] = (AwakenedForgeRecipe.type,)
	name: ClassVar[str] = "(Stardust Fragment) Awakened Forge"

	def static_glyph(self, craft: JsonDict) -> str:
		""" 3x3 or 3x4 forge template glyph, from the ingredient count.

		Called before the shapeless->shaped conversion, so ``ingredients`` is still the original list.
		"""
		return AWAKENED_3X3_FONT if len(craft["ingredients"]) <= 9 else AWAKENED_3X4_FONT

	def append_hover(self, r: RecipeRenderer, craft: JsonDict, hover: list[TextComponent]) -> None:
		""" Count + list every grid ingredient. """
		ingredients_hover(craft, hover)

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		""" Lay the ingredient grid out over the forge template, then place the result. """
		shape: list[str] = craft["shape"]
		is_small_craft: bool = len(shape) <= 3 and all(len(x) <= 3 for x in shape)
		if use_dialog and not is_small_craft:
			content[-1] = content[-1].replace(page_font, page_font + VERY_SMALL_NONE_FONT * 2)  # type: ignore
		formatted_ingredients: dict[str, JsonDict] = {k: r.item_component(v, count=v.get("count", 1)) for k, v in craft["ingredients"].items()}

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
					content.append(INVISIBLE_ITEM_WIDTH * max(0, (3 if is_small_craft else 4) - len(line)))
					if is_small_craft:
						content.append(NONE_FONT * 2)
					else:
						content.append(NONE_FONT + SMALL_NONE_FONT)
				content.append("\n")
		if len(shape) == 1 and len(shape[0]) < 3:
			content.append("\n")

		if is_small_craft:
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
		else:
			len_line = len(shape[1]) if len(shape) > 1 else 0
			offset = 4 - len_line
			break_line_pos = content.index("\n", content.index("\n") + 1)
			try:
				break_line_pos = content.index("\n", break_line_pos + 1)
			except Exception:
				content.append(SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1)) + MICRO_NONE_FONT)
			content.insert(break_line_pos + 1, result_component)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
				break_line_pos += 1
			try:
				break_line_pos = content.index("\n", break_line_pos + 3)
			except Exception:
				content.append("\n" + SMALL_NONE_FONT)
				break_line_pos = len(content)
			content.insert(break_line_pos, (INVISIBLE_ITEM_WIDTH * (offset - 1)) + MICRO_NONE_FONT)
			copy = result_component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.insert(break_line_pos + 1, copy)
			if use_dialog:
				content.insert(break_line_pos + 2, VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			if len(shape) < 3 and len(shape[0]) == 4:
				content.append("\n\n")
				if len(shape) < 2:
					content.append("\n")
		content.insert(3, "\n")


register_craft_renderer(AwakenedForgeRenderer())
