"""Single-row "ingredient -> result" renderers: stonecutting / pulverizing / mining."""

# ruff: noqa: E501
# Imports
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from .....core.cls.recipe import PulverizingRecipe, StonecuttingRecipe
from ...glyphs import (
	INVISIBLE_ITEM_WIDTH,
	MICRO_NONE_FONT,
	MINING_FONT,
	PULVERIZING_FONT,
	SMALL_NONE_FONT,
	STONECUTTING_FONT,
	VERY_SMALL_NONE_FONT,
)
from ..hovers import mining_hover
from ..registry import CraftRenderer, register_craft_renderer

if TYPE_CHECKING:
	from ..renderer import RecipeRenderer


# TODO: They should be dataclasses
class LinearRenderer(CraftRenderer):
	""" Shared single-row layout (ingredient on the left, result on the right). """

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		formatted_ingredient: JsonDict = r.item_component(craft["ingredient"], add_change_page=add_change_page_to_ingr)
		content.append("\n\n")
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			r.append_or_invisible(content, formatted_ingredient, i)
			content.append(SMALL_NONE_FONT * 4 + VERY_SMALL_NONE_FONT + INVISIBLE_ITEM_WIDTH)
			r.append_or_invisible(content, result_component, i)
			if use_dialog:
				content.append(VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			content.append("\n")
		content.append("\n")


class StonecuttingRenderer(LinearRenderer):
	types: ClassVar[tuple[str, ...]] = (StonecuttingRecipe.type,)
	name: ClassVar[str] = "Stonecutting"

	def static_glyph(self, craft: JsonDict) -> str:
		return STONECUTTING_FONT


class PulverizingRenderer(LinearRenderer):
	types: ClassVar[tuple[str, ...]] = (PulverizingRecipe.type,)
	name: ClassVar[str] = "(SimplEnergy) Pulverizing"

	def static_glyph(self, craft: JsonDict) -> str:
		return PULVERIZING_FONT


class MiningRenderer(LinearRenderer):
	""" Pseudo-recipe generated from no-silk-touch drops. """
	types: ClassVar[tuple[str, ...]] = ("mining",)
	name: ClassVar[str] = "Mining"

	def static_glyph(self, craft: JsonDict) -> str:
		return MINING_FONT

	def append_hover(self, r: RecipeRenderer, craft: JsonDict, hover: list[TextComponent]) -> None:
		mining_hover(craft, hover)


register_craft_renderer(StonecuttingRenderer())
register_craft_renderer(PulverizingRenderer())
register_craft_renderer(MiningRenderer())

