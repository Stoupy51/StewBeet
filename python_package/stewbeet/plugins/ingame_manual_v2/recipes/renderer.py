"""The :class:`RecipeRenderer` dispatcher.

Builds craft content, item hover components and wiki buttons for a manual by delegating each
recipe type to its registered :class:`~.registry.CraftRenderer`. Keeps the shared prologue and
button scaffolding; the per-type layout/hover/glyph/image live under :mod:`.types`.
"""

# Imports
from __future__ import annotations

from typing import TYPE_CHECKING

import stouputils as stp
from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ....core.__memory__ import Mem
from ....core.cls.block import Block, GrowingSeed
from ....core.cls.ingredients import Ingr
from ....core.cls.item import Item
from ....core.cls.recipe import CraftingShapelessRecipe
from ....core.utils.text_component import item_id_to_name
from ..glyphs import INVISIBLE_ITEM_WIDTH, MICRO_NONE_FONT, SMALL_NONE_FONT, WIKI_RESULT_OF_CRAFT_FONT
from ..refs import PageRef
from .buttons import WikiButtonRender
from .collection import collect_for_item, convert_shapeless_to_shaped
from .components import build_item_component, high_res_font_from_ingredient
from .registry import get_craft_renderer

if TYPE_CHECKING:
	from ..config import ManualConfig
	from ..glyphs import GlyphAllocator
	from ..images import GlyphImageBuilder
	from ..manual import Manual


class RecipeRenderer:
	""" Dispatcher: delegates per-type rendering to the registry, owns the shared scaffolding. """

	def __init__(self, manual: Manual) -> None:
		self.manual: Manual = manual

	@property
	def config(self) -> ManualConfig:
		return self.manual.config

	@property
	def glyphs(self) -> GlyphAllocator:
		return self.manual.glyphs

	@property
	def images(self) -> GlyphImageBuilder:
		return self.manual.images

	# --- delegated helpers ---
	def item_component(self, ingredient: str | Ingr, only_those_components: list[str] | None = None, count: int = 1, add_change_page: bool = True) -> JsonDict:
		""" Build a hoverable/clickable text component for an ingredient. """
		return build_item_component(self, ingredient, only_those_components, count, add_change_page)

	def high_res_font_from_ingredient(self, ingredient: str | Ingr, count: int = 1) -> str:
		""" Generate the high-res glyph for an ingredient. """
		return high_res_font_from_ingredient(self, ingredient, count)

	def collect_for_item(self, name: str, item_obj: Item, definitions_as_objects: dict[str, Item]) -> list[JsonDict]:
		""" Gather an item's own recipes, otherside crafts, and mining drops (deduped). """
		return collect_for_item(self, name, item_obj, definitions_as_objects)

	@staticmethod
	def append_or_invisible(content: list[TextComponent], component: JsonDict, i: int) -> None:
		""" Append ``component`` on the first row, an invisible-width copy on the second. """
		if i == 0:
			content.append(component)
		else:
			copy = component.copy()
			copy["text"] = INVISIBLE_ITEM_WIDTH
			content.append(copy)

	# --- main craft content ---
	def render_main(self, craft: JsonDict, name: str, page_font: str, in_lore: bool = False) -> list[TextComponent]:
		""" Build the full text-component layout for a single craft shown on a page. """
		craft_type = craft["type"]
		content: list[TextComponent] = [{"text": "", "font": self.config.font, "color": "white"}]

		if craft_type == "crafting_shapeless":
			craft = convert_shapeless_to_shaped(craft)
			craft_type = "crafting_shaped"

		renderer = get_craft_renderer(craft_type)
		if renderer is None:
			return content

		# static_glyph runs on the still-original craft (matters for awakened forge 3x3 vs 3x4)
		if self.config.high_resolution:
			page_font = renderer.static_glyph(craft)
		use_dialog: bool = self.config.use_dialog > 0 and not in_lore

		if craft_type == "stardust_awakened_forge":
			craft = convert_shapeless_to_shaped(craft)
			craft["type"] = "stardust_awakened_forge"

		titled = item_id_to_name(name) + "\n"
		content.append({"text": titled, "font": "minecraft:default", "color": "black", "underlined": True})
		padding: str = MICRO_NONE_FONT if use_dialog else ""
		content.append(SMALL_NONE_FONT + padding + page_font + "\n")

		renderer.build_image(self, name, page_font, craft)

		result_count = craft.get("result_count", 1)
		add_change_page_to_ingr: bool = False
		if not craft.get("result"):
			result_component = self.item_component(name, count=result_count, add_change_page=False)
			add_change_page_to_ingr = True
		else:
			add_change_page_to_ingr = Ingr(craft["result"]).to_id(add_namespace=False) == name
			result_component = self.item_component(craft["result"], count=result_count, add_change_page=not add_change_page_to_ingr)
		result_component["text"] = MICRO_NONE_FONT + result_component["text"]

		renderer.render_body(self, craft, name, content, result_component, page_font, use_dialog, add_change_page_to_ingr)
		return content

	# --- wiki button building ---
	def render_button(self, craft: JsonDict, name: str, index: int = 0) -> WikiButtonRender:
		""" Build a single wiki button (hover + icon + deferred target) for a craft.

		``index`` makes the low-resolution recipe image filename stable/unique per button.
		"""
		craft_for_button = craft
		if craft["type"] == CraftingShapelessRecipe.type:
			craft_for_button = convert_shapeless_to_shaped(craft)

		breaklines = 3
		if "shape" in craft_for_button:
			breaklines = max(2, max(len(craft_for_button["shape"]), len(craft_for_button["shape"][0])))

		if not self.config.high_resolution:
			craft_font = self.glyphs.allocate()
			btn_renderer = get_craft_renderer(craft_for_button["type"])
			if btn_renderer is not None:
				btn_renderer.build_image(self, name, craft_font, craft_for_button, output_name=f"{name}_{index + 1}")
			hover_text: list[TextComponent] = [{"text": ""}, {"text": craft_font + "\n\n" * breaklines, "font": self.config.font, "color": "white"}]
		else:
			from ..glyphs import HOVER_EQUIVALENTS
			from ..optimizer import remove_events
			craft_content: list[TextComponent] = self.render_main(craft_for_button, name, "", in_lore=True)
			craft_content = [craft_content[0], *craft_content[2:]]
			remove_events(craft_content)
			for k, v in HOVER_EQUIVALENTS.items():
				if isinstance(craft_content[1], str):
					craft_content[1] = craft_content[1].replace(k, v)
			hover_text = [{"text": ""}, craft_content]

		# Recipe type title + per-ingredient hover lines (delegated to the renderer)
		renderer = get_craft_renderer(craft["type"])
		if renderer is not None and renderer.name:
			hover_text.append({"text": f"\n{renderer.name}", "color": "yellow"})
		if renderer is not None:
			renderer.append_hover(self, craft, hover_text)

		glyph = WIKI_RESULT_OF_CRAFT_FONT if "result" not in craft else self.images.wiki_result_icon(name, craft)
		button = WikiButtonRender(glyph=glyph, hover=hover_text, priority=craft.get("manual_priority", 1) or 1)

		# Deferred target
		craft_result: str = "" if "result" not in craft else Ingr(craft["result"]).to_id(add_namespace=False)
		if craft_result and craft_result != name:
			if craft_result in Mem.definitions:
				button.target = PageRef(item=craft_result)
		else:
			craft_ingredient: str = ""
			if craft.get("ingredient"):
				craft_ingredient = Ingr(craft["ingredient"]).to_id(add_namespace=False)
			elif craft.get("ingredients") and stp.is_generic_instance(craft["ingredients"], list[stp.JsonDict]) and len(craft["ingredients"]) == 1:
				craft_ingredient = Ingr(craft["ingredients"][0]).to_id(add_namespace=False)
			elif craft.get("ingredients") and stp.is_generic_instance(craft["ingredients"], stp.JsonDict) and len(craft["ingredients"]) == 1:
				craft_ingredient = Ingr(next(iter(craft["ingredients"].values()))).to_id(add_namespace=False)
			button.blue_craft = craft_result == ""
			if craft_ingredient and craft_ingredient in Mem.definitions and craft_ingredient != name:
				button.target = PageRef(item=craft_ingredient)
		return button

	# --- growing seed info button (button-only pseudo, built from block metadata) ---
	def growing_seed_button(self, name: str, item_obj: Item) -> WikiButtonRender | None:
		""" Build an info button describing a block's :class:`GrowingSeed` drops, if any. """
		if not isinstance(item_obj, Block) or not item_obj.growing_seed:
			return None
		seed: GrowingSeed = item_obj.growing_seed

		hover: list[TextComponent] = [{"text": ""}, {"text": "\nGrowing Seed", "color": "yellow"}]
		planted = str(seed.planted_on).replace("minecraft:", "").replace("_", " ").title()
		hover.append({"text": "\n- Planted on: ", "color": "gray"})
		hover.append({"text": planted, "color": "gray"})
		minutes, secs = divmod(int(seed.seconds), 60)
		grow_time = f"{minutes}m {secs}s" if minutes else f"{secs}s"
		hover.append({"text": "\n- Grow time: ", "color": "gray"})
		hover.append({"text": grow_time, "color": "gray"})

		first_loot_id: str = ""
		if isinstance(seed.loots, str):
			hover.append({"text": "\n- Drops: variable (loot table)", "color": "gray"})
		else:
			hover.append({"text": "\n- Drops:", "color": "gray"})
			for loot in seed.loots:
				if not first_loot_id and ":" not in loot.id:
					first_loot_id = loot.id
				rolls = loot.rolls
				rolls_str = (f"{rolls.get('min', 1)}-{rolls.get('max', 1)}" if isinstance(rolls, dict) else str(rolls))
				loot_name = item_id_to_name(loot.id.split(":")[-1]) if ":" not in loot.id else Ingr(loot.id).to_name()
				hover.append({"text": f"\n  - x{rolls_str} ", "color": "gray"})
				hover.append({"text": loot_name, "color": "gray"})
				if loot.fortune:
					hover.append({"text": f" (fortune +{loot.fortune.get('extra', 0)} @ {loot.fortune.get('probability', 0)})", "color": "dark_gray"})

		# Icon: result icon of the first internal loot if possible, else generic result-of-craft font
		glyph = WIKI_RESULT_OF_CRAFT_FONT
		target: PageRef | None = None
		if first_loot_id:
			fake_craft: JsonDict = {"type": "growing_seed", "result": Ingr(first_loot_id, self.config.project_id)}
			glyph = self.images.wiki_result_icon(name, fake_craft)
			target = PageRef(item=first_loot_id)
		return WikiButtonRender(glyph=glyph, hover=hover, target=target, priority=1)
