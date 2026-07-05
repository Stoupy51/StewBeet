"""Per-item page.

Encapsulates the v1 ``encode_page`` item branch (main content selection + wiki buttons),
re-expressed on top of :class:`~..recipes.RecipeRenderer` and :class:`~..recipes.WikiButtonRender`,
with button placement driven by :class:`~.button_layout.ButtonLayout` and cross-page links
emitted as deferred :class:`~..refs.PageRef`.
"""

# Imports
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


@dataclass(kw_only=True)
class ItemPage(Page):
	""" A page describing a single item: its main recipe, then a grid of wiki buttons.

	After :meth:`prepare`, ``crafts`` and ``buttons`` are populated and can be inspected or
	mutated by ``on_item_page`` hooks before :meth:`build` runs.
	"""
	crafts: list[JsonDict] = field(default_factory=list[JsonDict])
	""" Every craft related to the item, gathered by :meth:`prepare`. """
	buttons: list[WikiButtonRender] = field(default_factory=list[WikiButtonRender])
	""" The wiki buttons rendered on the page (populated during :meth:`build`). """

	@classmethod
	def for_item(cls, item_id: str, **kwargs: Any) -> "ItemPage":
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
		recipes = manual.recipes
		config = manual.config
		content: list[TextComponent] = []
		titled = item_id_to_name(name) + "\n"
		crafts = list(self.crafts)

		# --- main content selection (ported from v1) ---
		content_added = False
		mining_crafts = [c for c in crafts if c.get("type") == "mining"]
		if mining_crafts:
			content += recipes.render_main(mining_crafts[0], name, "")
			content_added = True

		if not content_added:
			blue_crafts = [c for c in crafts if not c.get("result")]
			if blue_crafts:
				blue_crafts.sort(key=lambda c: c.get("result_count", 0), reverse=True)
				content += recipes.render_main(blue_crafts[0], name, "")
				content_added = True
			else:
				# Single item in a box
				page_font = manual.glyphs.allocate()
				manual.images.recipe_image(name, page_font)
				component = recipes.item_component(name)
				component["text"] = NONE_FONT * 2
				content.append({"text": "", "font": config.font, "color": "white"})
				content.append({"text": titled, "font": "minecraft:default", "color": "black", "underlined": True})
				content.append(page_font + "\n")
				for _ in range(4):
					content.append(copy.deepcopy(component))
					content.append("\n")
				content_added = True

		# End of the main craft content: ButtonLayout.position == "after_recipe" inserts here
		recipe_end: int = len(content)

		# --- wiki buttons ---
		info_buttons: list[WikiButtonRender] = []

		# Special hardcoded note for heavy_workbench
		if name == "heavy_workbench":
			content.append([
				{"text": "\nEvery recipe that uses custom items ", "font": "minecraft:default", "color": "black"},
				{"text": "must", "color": "red", "underlined": True},
				{"text": " be crafted using the Heavy Workbench."},
			])
		else:
			# WikiButton info buttons
			info_buttons += self.wiki_info_buttons(obj)

			# Growing seed info button (right after the other info buttons)
			gs_button = recipes.growing_seed_button(obj) if obj is not None else None
			if gs_button is not None:
				info_buttons.append(gs_button)

			# One button per craft (skip consecutive duplicate results)
			previous_result = None
			for idx, craft in enumerate(crafts):
				craft_for_check = convert_shapeless_to_shaped(craft) if craft["type"] == "crafting_shapeless" else craft
				current_result = craft_for_check.get("result")
				if current_result and current_result == previous_result and craft["type"] != "mining":
					continue
				previous_result = current_result
				info_buttons.append(recipes.render_button(craft, name, idx))

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
			found_event: JsonDict | None = None
			if isinstance(button_value, dict) and "click_event" in button_value:
				found_event = cast(JsonDict, button_value["click_event"])
			elif isinstance(button_value, list):
				for comp in button_value:
					if isinstance(comp, dict) and "click_event" in comp:
						found_event = cast(JsonDict, comp["click_event"])
						break
			out.append(WikiButtonRender(glyph=WIKI_INFO_FONT, hover=button_value, target=found_event, is_info=True))
		return out

	def apply_layout_filters(self, buttons: list[WikiButtonRender], layout: ButtonLayout) -> list[WikiButtonRender]:
		""" Apply include/order/extra + overflow handling (ported from v1). """
		buttons = list(buttons)
		if layout.include is not None:
			buttons = [b for b in buttons if layout.include(b)]
		buttons += list(layout.extra_buttons)
		if layout.order is not None:
			buttons.sort(key=layout.order)

		limit = layout.max_buttons
		if len(buttons) > limit:
			# Remove blue crafts except the last one (keep info buttons)
			has_info = bool(buttons and buttons[0].is_info)
			first_index = 1 if has_info else 0
			last_blue = -1
			for i, b in enumerate(buttons):
				if b.blue_craft and i != first_index:
					last_blue = i
			if (last_blue - first_index) > 1:
				buttons = buttons[:first_index] + buttons[last_blue:]
			while len(buttons) > limit:
				lowest = min(reversed(buttons), key=lambda b: b.priority)
				buttons.remove(lowest)
			buttons = buttons[:limit]
		return buttons

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
		self, content: list[TextComponent], buttons: list[WikiButtonRender], layout: ButtonLayout, manual: "Manual", recipe_end: int,
	) -> list[TextComponent]:
		""" Splice the button grid into ``content`` where ``layout.position`` asks for.

		``recipe_end`` is the index right after the main craft content. At this point ``content``
		still holds the in-body title at index 1 (dropped later by :meth:`build`), so "top"
		inserts at index 2.

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
