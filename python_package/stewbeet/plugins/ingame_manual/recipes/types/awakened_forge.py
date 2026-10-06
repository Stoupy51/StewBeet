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
	MICRO_NONE_FONT,
	NONE_FONT,
	SMALL_NONE_FONT,
	VERY_SMALL_NONE_FONT,
)
from ..grid import append_grid, centred_shape, place_result_beside
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
			content[-1] = content[-1].replace(page_font, page_font + VERY_SMALL_NONE_FONT * 2)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
		formatted_ingredients: dict[str, JsonDict] = {k: r.item_component(v, count=v.get("count", 1)) for k, v in craft["ingredients"].items()}
		shape = centred_shape(shape)
		filler: str | None = (NONE_FONT * 2 if is_small_craft else NONE_FONT + SMALL_NONE_FONT) if use_dialog else None
		append_grid(content, shape, formatted_ingredients, filler, columns=3 if is_small_craft else 4, small=is_small_craft)
		if is_small_craft:
			place_result_beside(content, shape, result_component, use_dialog, gap_end=SMALL_NONE_FONT * 2, full_width=3)
		else:
			place_result_beside(content, shape, result_component, use_dialog, gap_end=MICRO_NONE_FONT, full_width=4)
		content.insert(3, "\n")


register_craft_renderer(AwakenedForgeRenderer())

