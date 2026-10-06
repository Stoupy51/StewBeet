"""Per-item page.

Encapsulates the v1 ``encode_page`` item branch (main content selection + wiki buttons),
re-expressed on top of :class:`~..recipes.RecipeRenderer` and :class:`~..recipes.WikiButtonRender`,
with button placement driven by :class:`~.button_layout.ButtonLayout` and cross-page links
emitted as deferred :class:`~..refs.PageRef`.
"""

# Imports
from __future__ import annotations

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ....core.cls.item import Item
from ....core.cls.wiki_button import WikiButton
from ....core.constants import WIKI_COMPONENT
from ....core.utils.text_component import item_id_to_name
from ..button_layout import ButtonLayout
from ..glyphs import (
	NONE_FONT,
	VERY_SMALL_NONE_FONT,
	WIKI_INFO_FONT,
	WIKI_NONE_FONT,
)
from ..recipes import WikiButtonRender, convert_shapeless_to_shaped
from ..refs import PageRef
from .base import Page

if TYPE_CHECKING:
	from ..manual import Manual


@dataclass(kw_only=True, slots=True)
class ItemPage(Page):
	""" A page describing a single item: its main recipe, then a grid of wiki buttons.

	After :meth:`prepare`, ``crafts`` and ``buttons`` are populated and can be inspected or
	mutated by ``on_item_page`` hooks before :meth:`build` runs.
	"""
	crafts: list[JsonDict] = field(default_factory=list[JsonDict])
	""" Every craft related to the item, gathered by :meth:`prepare`. """
	buttons: list[WikiButtonRender] = field(default_factory=list[WikiButtonRender])
	""" The wiki buttons rendered on the page (populated during :meth:`build`). """
	extra_buttons: list[WikiButtonRender] = field(default_factory=list[WikiButtonRender])
	""" Developer-added buttons appended after the automatic ones,
	e.g. another item's recipe via ``manual.recipes.button_for_item(...)`` or a page link via ``manual.recipes.link_button(...)``. """

	@classmethod
	def for_item(cls, item_id: str, **kwargs: Any) -> ItemPage:
		""" Convenience constructor producing a page anchored at ``item:<id>``. """
		return cls(anchor=f"item:{item_id}", item_id=item_id, title=item_id_to_name(item_id), **kwargs)

	def prepare(self, manual: Manual) -> None:
		""" Collect this item's crafts (own recipes, otherside crafts, mining drops). """
		if self.item_id is None:
			return
		obj = manual.object_for(self.item_id)
		if obj is None:
			return
		self.crafts = manual.recipes.collect_for_item(self.item_id, obj, manual.definitions_as_objects)

	def build(self, manual: Manual) -> list[TextComponent]:
		""" Render the main recipe (or single-item box) followed by the wiki-button grid. """
		name = self.item_id or self.anchor
		obj = manual.object_for(name)
		content: list[TextComponent] = self.main_content(manual, name)

		# End of the main craft content: ButtonLayout.position == "after_recipe" inserts here
		recipe_end: int = len(content)
		info_buttons: list[WikiButtonRender] = []
		if name == "heavy_workbench":
			content.append([
				{"text": "\nEvery recipe that uses custom items ", "font": "minecraft:default", "color": "black"},
				{"text": "must", "color": "red", "underlined": True},
				{"text": " be crafted using the Heavy Workbench."},
			])
		else:
			info_buttons = self.craft_buttons(manual, name, obj)

		# Developer-added buttons (cross-page recipe buttons, page links...)
		info_buttons += self.extra_buttons

		# Combine with the page's button layout
		self.buttons = info_buttons
		layout = self.resolve_button_layout(manual)
		buttons = self.apply_layout_filters(info_buttons, layout)
		if buttons:
			content = self.place_button_grid(content, buttons, layout, manual, recipe_end)

		# Drop the in-body title (the dialog shows it from the page/sprite) and disable text
		# shadow on the page's base style. content[0] is the manual-font setter, content[1] the title.
		content = [content[0], *content[2:]]
		if isinstance(content[0], dict):
			content[0] = {**content[0], "shadow_color": [0,0,0,0]}
		return content

	def main_content(self, manual: Manual, name: str) -> list[TextComponent]:
		""" The page's main craft: how the item is mined, else the craft using most of it, else the item alone in a box. """
		crafts: list[JsonDict] = list(self.crafts)
		mining_crafts: list[JsonDict] = [c for c in crafts if c.get("type") == "mining"]
		if mining_crafts:
			return list(manual.recipes.render_main(mining_crafts[0], name, ""))
		blue_crafts: list[JsonDict] = [c for c in crafts if not c.get("result")]
		if blue_crafts:
			blue_crafts.sort(key=lambda c: c.get("result_count", 0), reverse=True)
			return list(manual.recipes.render_main(blue_crafts[0], name, ""))

		page_font = manual.glyphs.allocate()
		manual.images.recipe_image(name, page_font)
		component = manual.recipes.item_component(name)
		component["text"] = NONE_FONT * 2
		content: list[TextComponent] = [
			{"text": "", "font": manual.config.font, "color": "white"},
			{"text": item_id_to_name(name) + "\n", "font": "minecraft:default", "color": "black", "underlined": True},
			page_font + "\n",
		]
		for _ in range(4):
			content.append(copy.deepcopy(component))
			content.append("\n")
		return content

	def craft_buttons(self, manual: Manual, name: str, obj: Item | None) -> list[WikiButtonRender]:
		""" The item's info buttons, its growing seed button, then a button per craft, skipping a repeat of the previous result. """
		buttons: list[WikiButtonRender] = self.wiki_info_buttons(obj)
		gs_button = manual.recipes.growing_seed_button(obj) if obj is not None else None
		if gs_button is not None:
			buttons.append(gs_button)

		previous_result = None
		for idx, craft in enumerate(self.crafts):
			craft_for_check = convert_shapeless_to_shaped(craft) if craft["type"] == "crafting_shapeless" else craft
			current_result = craft_for_check.get("result")
			if current_result and current_result == previous_result and craft["type"] != "mining":
				continue
			previous_result = current_result
			buttons.append(manual.recipes.render_button(craft, name, idx))
		return buttons

	# --- helpers ---
	def wiki_info_buttons(self, obj: Item | None) -> list[WikiButtonRender]:
		""" Build info buttons from the item's WIKI_COMPONENT (WikiButton list or raw text). """
		out: list[WikiButtonRender] = []
		if obj is None or not obj.get(WIKI_COMPONENT):
			return out
		wiki_component: TextComponent | list[WikiButton] = obj[WIKI_COMPONENT]
		is_list_of_buttons: bool = isinstance(wiki_component, list) and any(isinstance(c, WikiButton) for c in wiki_component)  # type: ignore[arg-type]
		wiki_buttons: list[TextComponent] = wiki_component if is_list_of_buttons else [wiki_component]  # type: ignore[assignment, list-item]
		for button in wiki_buttons:
			button_value: TextComponent = button.to_dict() if isinstance(button, WikiButton) else button  # type: ignore[redundant-expr]
			event: JsonDict | None = self.click_event_of(button_value)
			out.append(WikiButtonRender(glyph=WIKI_INFO_FONT, hover=button_value, target=event, is_info=True))
		return out

	@staticmethod
	def click_event_of(component: TextComponent) -> JsonDict | None:
		""" The click event of a text component, or of the first part of one that has one. """
		if isinstance(component, dict):
			return cast(JsonDict, component["click_event"]) if "click_event" in component else None
		if isinstance(component, list):
			events = (cast(JsonDict, part["click_event"]) for part in component if isinstance(part, dict) and "click_event" in part)
			return next(events, None)
		return None

	def apply_layout_filters(self, buttons: list[WikiButtonRender], layout: ButtonLayout) -> list[WikiButtonRender]:
		""" Apply the layout's include, extra buttons and order, then trim to its maximum. """
		buttons = list(buttons)
		if layout.include is not None:
			buttons = [b for b in buttons if layout.include(b)]
		buttons += list(layout.extra_buttons)
		if layout.order is not None:
			buttons.sort(key=layout.order)
		return self.trimmed(buttons, layout.max_buttons) if len(buttons) > layout.max_buttons else buttons

	@staticmethod
	def trimmed(buttons: list[WikiButtonRender], limit: int) -> list[WikiButtonRender]:
		""" Buttons cut down to `limit`: the blue crafts but the last one go first, info buttons kept, then the lowest priorities. """
		first_index: int = 1 if buttons and buttons[0].is_info else 0
		last_blue: int = max((i for i, b in enumerate(buttons) if b.blue_craft and i != first_index), default=-1)
		if (last_blue - first_index) > 1:
			buttons = buttons[:first_index] + buttons[last_blue:]
		while len(buttons) > limit:
			buttons.remove(min(reversed(buttons), key=lambda b: b.priority))
		return buttons[:limit]

	def button_to_component(self, button: WikiButtonRender) -> JsonDict:
		""" Convert a button to its visible text component (icon + hover + optional click). """
		component: JsonDict = {
			"text": button.glyph + VERY_SMALL_NONE_FONT * 2,
			"hover_event": {"action": "show_text", "value": button.hover},
		}
		if isinstance(button.target, PageRef):
			component["click_event"] = {"action": "change_page", "page": button.target}
		elif isinstance(button.target, dict):
			component["click_event"] = button.target
		return component

	def place_button_grid(
		self, content: list[TextComponent], buttons: list[WikiButtonRender], layout: ButtonLayout, manual: Manual, recipe_end: int,
	) -> list[TextComponent]:
		""" Splice the button grid into ``content`` where ``layout.position`` asks for.

		``recipe_end`` is the index right after the main craft content.
		At this point ``content`` still holds the in-body title at index 1 (dropped later by :meth:`build`),
		so "top" inserts at index 2.

		>>> layout = ButtonLayout(position=lambda content, buttons, manual: [*content, "grid"])
		>>> ItemPage(anchor="item:demo").place_button_grid(["base"], [], layout, None, 1)
		['base', 'grid']
		"""
		position = layout.position
		if callable(position):
			return position(content, buttons, manual)
		grid: list[TextComponent] = []
		self.render_button_grid(grid, buttons, layout)
		if position == "top":
			index = min(2, len(content))
			grid.append("\n")
		elif position == "after_recipe":
			index = recipe_end
		elif position == "bottom":
			index = len(content)
		else:
			raise ValueError(f"Unknown ButtonLayout.position: {position!r} (expected 'after_recipe', 'top', 'bottom', or a callable)")
		content[index:index] = grid
		return content

	def render_button_grid(self, content: list[TextComponent], buttons: list[WikiButtonRender], layout: ButtonLayout) -> None:
		""" Lay buttons into a grid, duplicating each line for the 2-row hover trick (ported). """
		content.append("\n")
		columns = max(1, layout.columns)
		components = [self.button_to_component(b) for b in buttons]

		last_i = 0
		for i, comp in enumerate(components):
			last_i = i
			if i % columns == 0 and i != 0:
				# Remove trailing spacer from the previous line to avoid an automatic break
				last_content = cast(JsonDict, content[-1])
				last_content["text"] = last_content["text"].replace(VERY_SMALL_NONE_FONT, "")
				# Re-add the previous row with the wiki spacer glyph (second visual row, same hovers)
				content += ["\n"] + [cast(JsonDict, x).copy() for x in content[-columns:]]
				for j in range(columns):
					selected = cast(JsonDict, content[-columns + j])
					selected["text"] = WIKI_NONE_FONT + VERY_SMALL_NONE_FONT * (2 if j != (columns - 1) else 0)
				content.append("\n")
			content.append(comp)

		# Duplicate the final (partial) row
		if last_i % columns != 0 or last_i == 0:
			last_i = last_i % columns + 1
			last_content = cast(JsonDict, content[-1])
			last_content["text"] = last_content["text"].replace(VERY_SMALL_NONE_FONT, "")
			content += ["\n"] + [cast(JsonDict, x).copy() for x in content[-last_i:]]
			for j in range(last_i):
				selected = cast(JsonDict, content[-last_i + j])
				selected["text"] = WIKI_NONE_FONT + VERY_SMALL_NONE_FONT * (2 if j != (last_i - 1) else 0)

