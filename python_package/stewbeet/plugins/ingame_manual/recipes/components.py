"""Item hover/click component builder.

Cross-page links are emitted as deferred :class:`~..refs.PageRef` page values.
Functions take the :class:`~.renderer.RecipeRenderer` dispatcher ``r`` for config/glyphs/images access.
"""

# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import os
from typing import TYPE_CHECKING

import stouputils as stp
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.ingredients import Ingr
from ....core.cls.item import Item
from ..glyphs import NONE_FONT
from ..refs import PageRef

if TYPE_CHECKING:
	from .renderer import RecipeRenderer


def high_res_font_from_ingredient(r: RecipeRenderer, ingredient: str | Ingr, count: int = 1) -> str:
	""" Generate the high-res glyph for an ingredient (by id or Ingr). """
	if isinstance(ingredient, dict):
		ingr_str: str = Ingr(ingredient).to_id(add_namespace=True)
	else:
		ingr_str = ingredient
	renders_path = r.config.iso_renders_path
	if ':' in ingr_str:
		item_image: Image.Image = open_render(f"{renders_path}/{ingr_str.replace(':', '/')}.png")
		ingr_str = ingr_str.split(":")[1]
	else:
		item_image = open_render(f"{renders_path}/{r.config.project_id}/{ingr_str}.png")
	return r.images.high_res_icon(ingr_str, item_image, count)


def open_render(path: str) -> Image.Image:
	""" The render at `path`, or a transparent 16x16 placeholder with a warning when it is missing. """
	if not os.path.exists(path):
		stp.warning(f"Missing texture at '{path}', using placeholder texture")
		return Image.new("RGBA", (16, 16), (255, 255, 255, 0))
	return Image.open(path)


def build_item_component(
	r: RecipeRenderer,
	ingredient: str | Ingr,
	only_those_components: list[str] | None = None,
	count: int = 1,
	add_change_page: bool = True,
) -> JsonDict:
	""" Build a hoverable/clickable text component for an ingredient. """
	use_dialog: bool = r.config.use_dialog > 0
	if only_those_components is None or use_dialog:
		only_those_components = []

	formatted: TextComponent = {
		"text": NONE_FONT,
		"hover_event": {"action": "show_item", "id": ""},
	}
	if isinstance(ingredient, dict) and ingredient.get("item"):
		formatted["hover_event"]["id"] = ingredient["item"]
	else:
		if not isinstance(ingredient, str):
			ingredient = Ingr(ingredient)
		id, obj = definition_of(r, ingredient)
		if not obj:
			stp.error("Item not found in definitions or external definitions: " + str(ingredient))
			return formatted

		formatted["hover_event"]["id"] = obj.base_item.replace("minecraft:", "")
		# Only emit the components map when non-empty (an empty {} is heavy and useless)
		components: JsonDict = hover_components(r, obj, only_those_components, use_dialog=use_dialog)
		if components:
			formatted["hover_event"]["components"] = components

		# Deferred link to the item's page (resolved after ordering; dropped if absent)
		if add_change_page and ":" not in id:
			formatted["click_event"] = {"action": "change_page", "page": PageRef(item=id)}

	if r.config.high_resolution:
		formatted["text"] = high_res_font_from_ingredient(r, ingredient, count)
	return formatted


def definition_of(r: RecipeRenderer, ingredient: str | Ingr) -> tuple[str, Item | None]:
	""" An ingredient's id, and its definition among this pack's items or a dependency's, None when neither has it. """
	if isinstance(ingredient, str):
		return ingredient, Item.from_id(ingredient)

	# If the custom data of the ingredient is a reference to a definition in this pack, return it.
	custom_data: JsonDict = ingredient["components"]["minecraft:custom_data"]
	id: str = ingredient.to_id(add_namespace=False)
	if custom_data.get(r.config.project_id):
		return id, Item.from_id(id) if id in Mem.definitions else None

	# If the custom data of the ingredient is a reference to a definition in a dependency pack, return it.
	ns: str = next(iter(custom_data.keys())) + ":"
	for data in custom_data.values():
		item_id: str = ns + next(iter(data.keys()))
		if item_id in Mem.external_definitions:
			return id, Item.from_id(item_id)

	return id, None


def hover_components(r: RecipeRenderer, obj: Item, only_those_components: list[str], use_dialog: bool) -> JsonDict:
	""" The components an item shows on hover: those asked for, every one in a dialog, else the configured ones. """
	if only_those_components:
		return {key: obj.components[key] for key in only_those_components if key in obj.components}
	if use_dialog:
		return dict(obj.components)
	return {key: value for key, value in obj.components.items() if key in r.config.components_to_include}

