"""Emit helpers for :class:`~.manual.Manual` (static assets, font/texture output, manual item).

Extracted from ``manual.py`` to keep the orchestrator focused on the pipeline. Each function
takes the :class:`~.manual.Manual` instance.
"""

# Imports
import os
from pathlib import Path
from typing import TYPE_CHECKING

import stouputils as stp
from beet import Font, Texture

from ...core.__memory__ import Mem
from ...core.cls.item import Item
from .glyphs import (
	AWAKENED_3X3_FONT,
	AWAKENED_3X4_FONT,
	AWAKENED_FORGE_STRUCT_FONT,
	BOOK_FONT,
	FURNACE_FONT,
	HOME_FONT,
	HOVER_AWAKENED_3X3_FONT,
	HOVER_AWAKENED_3X4_FONT,
	HOVER_FURNACE_FONT,
	HOVER_MINING_FONT,
	HOVER_PULVERIZING_FONT,
	HOVER_SHAPED_2X2_FONT,
	HOVER_SHAPED_3X3_FONT,
	HOVER_STONECUTTING_FONT,
	INVISIBLE_ITEM_FONT,
	MEDIUM_NONE_FONT,
	MICRO_NONE_FONT,
	MINING_FONT,
	NONE_FONT,
	PULVERIZING_FONT,
	SHAPED_2X2_FONT,
	SHAPED_3X3_FONT,
	SMALL_NONE_FONT,
	STONECUTTING_FONT,
	VERY_SMALL_NONE_FONT,
	WIKI_GROWING_SEED_FONT,
	WIKI_INFO_FONT,
	WIKI_INGR_OF_CRAFT_FONT,
	WIKI_NONE_FONT,
	WIKI_RESULT_OF_CRAFT_FONT,
)
from .paths import TEMPLATES_PATH

if TYPE_CHECKING:
	from .manual import Manual


def register_static_assets(manual: Manual) -> None:
	""" Copy reserved template textures to the RP and register their providers. """
	ns = manual.config.project_id
	assets = Mem.ctx.assets[ns]

	def tex(name: str, src: str) -> None:
		assets.textures[name] = Texture(source_path=f"{TEMPLATES_PATH}/{src}")

	# Reserved textures
	if not manual.config.debug_mode:
		tex("font/none", "none_release.png")
		tex("font/invisible_item", "invisible_item_release.png")
	else:
		tex("font/none", "none.png")
		tex("font/invisible_item", "invisible_item.png")
	tex("font/wiki_information", "wiki_information.png")
	tex("font/wiki_growing_seed", "wiki_growing_seed.png")
	tex("font/wiki_result_of_craft", "wiki_result_of_craft.png")
	tex("font/wiki_ingredient_of_craft", "wiki_ingredient_of_craft.png")
	if manual.config.high_resolution:
		for n in ("shaped_2x2", "shaped_3x3", "furnace", "stonecutting", "pulverizing", "mining"):
			tex(f"font/{n}", f"{n}.png")
		if manual.has_forge_3x3:
			tex("font/awakened_forge_3x3", "awakened_forge_3x3.png")
		if manual.has_forge_3x4:
			tex("font/awakened_forge_3x4", "awakened_forge_3x4.png")
		if manual.has_forge_3x3 or manual.has_forge_3x4:
			tex("font/awakened_forge_1", "awakened_forge_1.png")
			tex("font/awakened_forge_2", "awakened_forge_2.png")
	tex("font/book", "book.png")  # dialog-first: always needed
	tex("font/home", "home.png")  # dialog "go to first page" arrow (texture is user-overridable)

	# Reserved providers (ported verbatim for alignment)
	add = manual.glyphs.add_provider

	def f(n: str) -> str:
		return f"{ns}:font/{n}.png"
	add(NONE_FONT, f("none"), 8, 20)
	add(MEDIUM_NONE_FONT, f("none"), 8, 18)
	add(SMALL_NONE_FONT, f("none"), 7, 7)
	add(VERY_SMALL_NONE_FONT, f("none"), 0, 2)
	add(MICRO_NONE_FONT, f("none"), 0, 1)
	add(WIKI_NONE_FONT, f("none"), 7, 16)
	add(INVISIBLE_ITEM_FONT, f("invisible_item"), 7, 16)
	add(WIKI_INFO_FONT, f("wiki_information"), 8, 16)
	add(WIKI_GROWING_SEED_FONT, f("wiki_growing_seed"), 8, 16)
	add(WIKI_RESULT_OF_CRAFT_FONT, f("wiki_result_of_craft"), 8, 16)
	add(WIKI_INGR_OF_CRAFT_FONT, f("wiki_ingredient_of_craft"), 8, 16)
	if manual.config.high_resolution:
		add(SHAPED_3X3_FONT, f("shaped_3x3"), 1, 58)
		add(SHAPED_2X2_FONT, f("shaped_2x2"), 1, 58)
		add(FURNACE_FONT, f("furnace"), 1, 58)
		add(STONECUTTING_FONT, f("stonecutting"), 4, 58)
		add(PULVERIZING_FONT, f("pulverizing"), 4, 58)
		add(MINING_FONT, f("mining"), 4, 58)
		add(HOVER_SHAPED_3X3_FONT, f("shaped_3x3"), -4, 58)
		add(HOVER_SHAPED_2X2_FONT, f("shaped_2x2"), -2, 58)
		add(HOVER_FURNACE_FONT, f("furnace"), -3, 58)
		add(HOVER_STONECUTTING_FONT, f("stonecutting"), -3, 58)
		add(HOVER_PULVERIZING_FONT, f("pulverizing"), -3, 58)
		add(HOVER_MINING_FONT, f("mining"), -3, 58)
		if manual.has_forge_3x3:
			add(AWAKENED_3X3_FONT, f("awakened_forge_3x3"), 9, 74)
			add(HOVER_AWAKENED_3X3_FONT, f("awakened_forge_3x3"), 4, 74)
		if manual.has_forge_3x4:
			add(AWAKENED_3X4_FONT, f("awakened_forge_3x4"), 9, 74)
			add(HOVER_AWAKENED_3X4_FONT, f("awakened_forge_3x4"), 4, 74)
		if manual.has_forge_3x3 or manual.has_forge_3x4:
			add(AWAKENED_FORGE_STRUCT_FONT[0], f("awakened_forge_1"), 8, 56)
			add(AWAKENED_FORGE_STRUCT_FONT[1], f("awakened_forge_2"), 8, 56)
	add(BOOK_FONT, f("book"), 25, 300)
	add(HOME_FONT, f("home"), 8, 20)  # same advance as NONE_FONT so the prev/next gap stays aligned


def write_font(manual: Manual) -> None:
	""" Write ``manual.json`` and register the font in the resource pack. """
	os.makedirs(f"{manual.config.cache_path}/font", exist_ok=True)
	with stp.super_open(f"{manual.config.cache_path}/font/manual.json", "w") as fh:
		fh.write(stp.json_dump(manual.glyphs.to_font_json()))
	Mem.ctx.assets[manual.config.project_id].fonts["manual"] = Font(source_path=f"{manual.config.cache_path}/font/manual.json")


def copy_generated_textures(manual: Manual) -> None:
	""" Copy every generated font PNG into the resource pack. """
	ns = manual.config.project_id
	folders = ["category", "page", "wiki_icons", *(["high_res"] if manual.config.high_resolution else [])]
	for folder in folders:
		folder_path = f"{manual.config.cache_path}/font/{folder}"
		if not os.path.isdir(folder_path):
			continue
		for file in os.listdir(folder_path):
			file_path = f"{folder_path}/{file}"
			no_extension = os.path.splitext(file)[0]
			if file.endswith(".png") and os.path.isfile(file_path):
				Mem.ctx.assets[ns].textures[f"font/{folder}/{no_extension}"] = Texture(source_path=file_path)


def validate_providers(manual: Manual) -> None:
	""" Error out if any font provider references a missing texture or has no chars. """
	ns = manual.config.project_id
	for fp in manual.glyphs.providers:
		if "file" in fp:
			path: str = os.path.splitext(fp["file"].split(":", 1)[-1])[0]
			if not Mem.ctx.assets[ns].textures.get(path):
				stp.error(f"Missing font provider at '{path}' for {fp}")
			if len(fp["chars"]) < 1 or (len(fp["chars"]) == 1 and not fp["chars"][0]):
				stp.error(f"Font provider '{path}' has no chars")


def create_manual_item(manual: Manual) -> None:
	""" Create/merge the ``manual`` item (dialog-first: no written_book NBT). """
	from ...core.definitions_helper import add_item_name_and_lore_if_missing
	from ...core.definitions_helper.completion import add_private_custom_data_for_namespace
	from ...core.utils.io import super_merge_dict
	from ..custom_recipes.vanilla import VanillaRecipeHandler
	from ..resource_pack.item_models.object import AutoModel

	if manual.config.use_dialog == 2 and "manual" not in Mem.definitions:
		return  # dialog-only, no item requested

	ns = manual.config.project_id
	manual_already_exists = "manual" in Mem.definitions
	manual_obj = Item(
		id="manual",
		base_item="minecraft:written_book",
		components={
			"item_model": f"{ns}:manual",
			"item_name": manual.config.name,
			"enchantment_glint_override": False,
			"max_stack_size": 16,
			"lore": [{"text": f"by {manual.config.project_author}", "color": "gray", "italic": False}],
		},
	)
	if manual_already_exists:
		current_def: Item = Item.from_id("manual")
		current_def.components = super_merge_dict(manual_obj.components, current_def.components)
		current_def.base_item = manual_obj.base_item
		Mem.definitions["manual"] = current_def
	add_item_name_and_lore_if_missing(black_list=[item for item in Mem.definitions if item != "manual"])
	add_private_custom_data_for_namespace(black_list=[item for item in Mem.definitions if item != "manual"])

	if not manual_already_exists:
		textures_folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
		textures: dict[str, str] = {
			stp.clean_path(str(p)).split("/")[-1]: stp.relative_path(str(p))
			for p in Path(textures_folder).rglob("*.png")
		}
		AutoModel.from_definitions(manual_obj, textures).process()
	VanillaRecipeHandler().generate_recipes(override=["manual"])

