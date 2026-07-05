"""Item hover/click component builder (ported from v1 ``book_components.get_item_component``).

Cross-page links are emitted as deferred :class:`~..refs.PageRef` page values. Functions take
the :class:`~.renderer.RecipeRenderer` dispatcher ``r`` for config/glyphs/images access.
"""

# Imports
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
	cache_path = r.config.cache_path
	if ':' in ingr_str:
		image_path = f"{cache_path}/items/{ingr_str.replace(':', '/')}.png"
		if not os.path.exists(image_path):
			stp.warning(f"Missing texture at '{image_path}', using placeholder texture")
			item_image = Image.new("RGBA", (16, 16), (255, 255, 255, 0))
		else:
			item_image = Image.open(image_path)
		ingr_str = ingr_str.split(":")[1]
	else:
		path: str = f"{cache_path}/items/{r.config.project_id}/{ingr_str}.png"
		if not os.path.exists(path):
			stp.warning(f"Missing texture at '{path}', using placeholder texture")
			item_image = Image.new("RGBA", (16, 16), (255, 255, 255, 0))
		else:
			item_image = Image.open(path)
	return r.images.high_res_icon(ingr_str, item_image, count)


def build_item_component(r: RecipeRenderer, ingredient: str | Ingr, only_those_components: list[str] | None = None, count: int = 1, add_change_page: bool = True) -> JsonDict:
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
		obj: Item | None = None
		if isinstance(ingredient, str):
			id = ingredient
			obj = Item.from_id(ingredient)
		else:
			ingredient = Ingr(ingredient)
			custom_data: JsonDict = ingredient["components"]["minecraft:custom_data"]
			id = ingredient.to_id(add_namespace=False)
			if custom_data.get(r.config.project_id):
				if id in Mem.definitions:
					obj = Item.from_id(id)
			else:
				ns = next(iter(custom_data.keys())) + ":"
				for data in custom_data.values():
					item_id = ns + next(iter(data.keys()))
					if item_id not in Mem.external_definitions:
						continue
					obj = Item.from_id(item_id)
					break
		if not obj:
			stp.error("Item not found in definitions or external definitions: " + str(ingredient))
			return formatted

		formatted["hover_event"]["id"] = obj.base_item.replace("minecraft:", "")
		components: JsonDict = {}
		if only_those_components:
			for key in only_those_components:
				if key in obj.components:
					components[key] = obj.components[key]
		elif not use_dialog:
			for key, value in obj.components.items():
				if key in r.config.components_to_include:
					components[key] = value
		else:
			for key, value in obj.components.items():
				components[key] = value
		# Only emit the components map when non-empty (an empty {} is heavy and useless)
		if components:
			formatted["hover_event"]["components"] = components

		# Deferred link to the item's page (resolved after ordering; dropped if absent)
		if add_change_page and ":" not in id:
			formatted["click_event"] = {"action": "change_page", "page": PageRef(item=id)}

	if r.config.high_resolution:
		formatted["text"] = high_res_font_from_ingredient(r, ingredient, count)
	return formatted

