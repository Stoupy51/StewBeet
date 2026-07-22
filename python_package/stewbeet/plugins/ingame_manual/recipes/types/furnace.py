"""Furnace-family renderers: smelting / blasting / smoking / campfire cooking."""

# ruff: noqa: E501
# Imports
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from .....core.cls.ingredients import Ingr
from .....core.cls.recipe import BlastingRecipe, CampfireCookingRecipe, SmeltingRecipe, SmokingRecipe
from ...glyphs import FURNACE_FONT, INVISIBLE_ITEM_WIDTH, MICRO_NONE_FONT, SMALL_NONE_FONT, VERY_SMALL_NONE_FONT
from ...paths import TEMPLATES_PATH
from ..registry import CraftRenderer, register_craft_renderer

if TYPE_CHECKING:
	from ..renderer import RecipeRenderer


@dataclass(slots=True)
class FurnaceBase(CraftRenderer):
	""" Shared layout/glyph/image for all furnace recipes (uses the default single-ingredient hover). """

	def static_glyph(self, craft: JsonDict) -> str:
		""" The furnace template glyph (same for the whole furnace family). """
		return FURNACE_FONT

	def render_body(self, r: RecipeRenderer, craft: JsonDict, name: str, content: list[TextComponent], result_component: JsonDict, page_font: str, use_dialog: bool, add_change_page_to_ingr: bool) -> None:
		""" Ingredient on top of the furnace, result on the output slot. """
		formatted_ingredient: JsonDict = r.item_component(craft["ingredient"], add_change_page=add_change_page_to_ingr)
		for i in range(2):
			content.append(SMALL_NONE_FONT)
			if i == 0:
				content.append(formatted_ingredient)
			else:
				copy = formatted_ingredient.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)
			content.append("\n")
		for i in range(2):
			content.append(SMALL_NONE_FONT * 4 + INVISIBLE_ITEM_WIDTH * 2)
			if i == 0:
				content.append(result_component)
			else:
				copy = result_component.copy()
				copy["text"] = INVISIBLE_ITEM_WIDTH
				content.append(copy)
			if use_dialog:
				content.append(VERY_SMALL_NONE_FONT + MICRO_NONE_FONT)
			content.append("\n")
		content.append("\n\n")

	def build_image(self, r: RecipeRenderer, name: str, page_font: str, craft: JsonDict, output_name: str = "") -> None:
		""" Low-resolution PNG of the ingredient + result pasted onto the furnace template. """
		if r.config.high_resolution:
			return
		output_filename = output_name or name
		result_texture, result_mask = r.images.load_result_texture(name, craft)
		template = Image.open(f"{TEMPLATES_PATH}/furnace.png")
		r.glyphs.add_provider(page_font, f"{r.config.project_id}:font/page/{output_filename}.png", ascent=0 if not output_name else 6, height=60)
		input_item: str = Ingr(craft["ingredient"]).to_id().replace(":", "/")
		item_texture = r.images.load_square_texture(input_item)
		template.paste(item_texture, (4, 4), item_texture.convert("RGBA").split()[3])
		coords = (124, 40)
		template.paste(result_texture, coords, result_mask)
		if craft["result_count"] > 1:
			count_img = r.images.image_count(craft["result_count"])
			template.paste(count_img, [x + 2 for x in coords], count_img)  # type: ignore
		template.save(f"{r.config.cache_path}/font/page/{output_filename}.png")


@dataclass(slots=True)
class SmeltingRenderer(FurnaceBase):
	""" ``smelting`` recipes (regular furnace). """
	types: ClassVar[tuple[str, ...]] = (SmeltingRecipe.type,)
	name: ClassVar[str] = "Smelting"


@dataclass(slots=True)
class BlastingRenderer(FurnaceBase):
	""" ``blasting`` recipes (blast furnace). """
	types: ClassVar[tuple[str, ...]] = (BlastingRecipe.type,)
	name: ClassVar[str] = "Blasting"


@dataclass(slots=True)
class SmokingRenderer(FurnaceBase):
	""" ``smoking`` recipes (smoker). """
	types: ClassVar[tuple[str, ...]] = (SmokingRecipe.type,)
	name: ClassVar[str] = "Smoking"


@dataclass(slots=True)
class CampfireRenderer(FurnaceBase):
	""" ``campfire_cooking`` recipes. """
	types: ClassVar[tuple[str, ...]] = (CampfireCookingRecipe.type,)
	name: ClassVar[str] = "Campfire Cooking"


register_craft_renderer(SmeltingRenderer())
register_craft_renderer(BlastingRenderer())
register_craft_renderer(SmokingRenderer())
register_craft_renderer(CampfireRenderer())
