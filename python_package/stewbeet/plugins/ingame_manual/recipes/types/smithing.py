"""Smithing renderers: smithing_transform / smithing_trim."""

# ruff: noqa: E501
# Imports
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from .....core.cls.recipe import SmithingTransformRecipe, SmithingTrimRecipe
from ...glyphs import INVISIBLE_ITEM_WIDTH, SMALL_NONE_FONT
from ..hovers import smithing_hover
from ..registry import CraftRenderer, register_craft_renderer

if TYPE_CHECKING:
	from ..renderer import RecipeRenderer


@dataclass
class SmithingTransformRenderer(CraftRenderer):
	""" ``smithing_transform`` recipes (base + template + addition -> result). """
	types: ClassVar[tuple[str, ...]] = (SmithingTransformRecipe.type,)
	name: ClassVar[str] = "Smithing Transform"

	def append_hover(self, r: RecipeRenderer, craft: JsonDict, hover: list[TextComponent]) -> None:
		""" Base / Template / Addition hover lines. """
		smithing_hover(craft, hover)

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		""" Base, template and addition in a row, then the result. """
		formatted_base: JsonDict = r.item_component(craft["base"])
		formatted_addition: JsonDict = r.item_component(craft["addition"])
		formatted_template: JsonDict = r.item_component(craft["template"])
		content.append("\n")
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			r.append_or_invisible(content, formatted_base, i)
			content.append(INVISIBLE_ITEM_WIDTH)
			r.append_or_invisible(content, formatted_template, i)
			content.append(INVISIBLE_ITEM_WIDTH)
			r.append_or_invisible(content, formatted_addition, i)
			content.append(SMALL_NONE_FONT + INVISIBLE_ITEM_WIDTH)
			r.append_or_invisible(content, result_component, i)
			content.append("\n")
		content.append("\n")


@dataclass
class SmithingTrimRenderer(CraftRenderer):
	""" ``smithing_trim`` recipes (no result item; the trim pattern slot is shown empty). """
	types: ClassVar[tuple[str, ...]] = (SmithingTrimRecipe.type,)
	name: ClassVar[str] = "Smithing Trim"

	def append_hover(self, r: RecipeRenderer, craft: JsonDict, hover: list[TextComponent]) -> None:
		""" Base / Template / Addition / Pattern hover lines. """
		smithing_hover(craft, hover)

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		""" Base, template and addition in a row, with an invisible pattern slot. """
		formatted_base: JsonDict = r.item_component(craft["base"])
		formatted_addition: JsonDict = r.item_component(craft["addition"])
		formatted_template: JsonDict = r.item_component(craft["template"])
		formatted_pattern: JsonDict = {"text": INVISIBLE_ITEM_WIDTH, "color": "white"}
		content.append("\n")
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			r.append_or_invisible(content, formatted_base, i)
			content.append(INVISIBLE_ITEM_WIDTH)
			r.append_or_invisible(content, formatted_template, i)
			content.append(INVISIBLE_ITEM_WIDTH)
			r.append_or_invisible(content, formatted_addition, i)
			content.append(INVISIBLE_ITEM_WIDTH)
			content.append(formatted_pattern)
			content.append("\n")
		content.append("\n")


register_craft_renderer(SmithingTransformRenderer())
register_craft_renderer(SmithingTrimRenderer())
