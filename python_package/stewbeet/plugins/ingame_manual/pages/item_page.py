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
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from beet.core.utils import TextComponent
from stouputils.typing import JsonDict

from ....core.cls.items.block import Block
from ....core.cls.items.item import Item
from ....core.cls.items.wiki_button import WikiButton
from ....core.cls.recipes.ingredients import Ingr
from ....core.constants import WIKI_COMPONENT
from ....core.utils.text_component import item_id_to_name
from ..button_layout import ButtonLayout, SideGrid
from ..config import ItemLayout
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

# Constants
BOX_ADVANCE: int = 41
""" Pixels the pen moves past the item's 40 pixel box, Minecraft adding one after the last opaque column. """

BOX_HEIGHT: int = 40
""" Pixels of the item's box, which hangs from the top of its line when ``box_offset`` is 0. """

LINE_HEIGHT: int = 9
""" Pixels between two lines of dialog text, Minecraft's font line height. """

LINE_BASELINE: int = 7
""" Pixels from the top of a line of text to its baseline, where a glyph of ascent 0 starts. """

BLANK_SLOT: str = WIKI_NONE_FONT + VERY_SMALL_NONE_FONT * 2
""" A button's place in a grid row with nothing in it: the blank button glyph and the spacing after it. """

SLOT_ADVANCE: int = 23
""" Pixels a button and the spacing after it take in a row: the 16 pixel glyph advances 17, each spacer 3. """

SPACING_ADVANCE: int = 6
""" Pixels of the spacing after a button, which the last button of a row goes without. """


@dataclass(kw_only=True, slots=True)
class ItemPage(Page):
	""" A page describing a single item: its main recipe, then a grid of wiki buttons.

	After :meth:`prepare`, ``crafts`` and ``buttons`` are populated and can be inspected or
	mutated by ``on_item_page`` hooks before :meth:`build` runs.
	"""
	crafts: list[JsonDict] = field(default_factory=list[JsonDict])
	""" Every craft related to the item, gathered by :meth:`prepare`. """
	main_craft: JsonDict | None = None
	""" A craft shown as the main recipe instead of the automatic choice, e.g. one of ``crafts``. """
	layout: ItemLayout | None = None
	""" What this page shows, None to follow ``ManualConfig.item_layout``. """
	box_gap: int | None = None
	""" Pixels between the box and the recipe in the ``"item+craft"`` layout, None to follow ``ManualConfig.item_box_gap``. """
	box_offset: int = 0
	""" Pixels moving the box down, negative to move it up, without moving the recipe beside it. """
	content_offset: tuple[int, int] = (0, 0)
	""" Pixels moving the box and the recipe right and down: x exactly, y in whole lines of text (9 pixels), rounded. """
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
		""" The content of :meth:`laid_out_content` moved by ``content_offset``.

		content[0] sets the manual font and content[1] is the title, so the lines to move start at content[2].
		"""
		content: list[TextComponent] = self.laid_out_content(manual, name)
		return [*content[:2], *self.moved(manual, content[2:], self.content_offset)]

	def laid_out_content(self, manual: Manual, name: str) -> list[TextComponent]:
		""" The page's main craft, the item alone in its box, or the box left of the craft, as the layout asks. """
		layout: ItemLayout = self.layout or manual.config.item_layout
		craft: JsonDict | None = None if layout == "item" else self.chosen_craft()
		if craft is None:
			return self.item_box(manual, name)

		content: list[TextComponent] = list(manual.recipes.render_main(craft, name, ""))
		if layout == "craft":
			return content
		gap: int = manual.config.item_box_gap if self.box_gap is None else self.box_gap
		return self.box_beside(manual, name, content, gap)

	def chosen_craft(self) -> JsonDict | None:
		""" The craft shown as the main recipe: ``main_craft``, else how the item is mined, else the craft using most of it. """
		if self.main_craft is not None:
			return self.main_craft
		mining_crafts: list[JsonDict] = [c for c in self.crafts if c.get("type") == "mining"]
		if mining_crafts:
			return mining_crafts[0]
		blue_crafts: list[JsonDict] = [c for c in self.crafts if not c.get("result")]
		return max(blue_crafts, key=lambda c: c.get("result_count", 0), default=None)

	def item_box(self, manual: Manual, name: str) -> list[TextComponent]:
		""" The item alone in its box, shown when it has no craft or the layout asks for it. """
		box, hover = self.box_glyph(manual, name)
		lines: list[int] = self.box_hover_lines()
		content: list[TextComponent] = [
			{"text": "", "font": manual.config.font, "color": "white"},
			{"text": item_id_to_name(name) + "\n", "font": "minecraft:default", "color": "black", "underlined": True},
			*([{**hover, "text": box}, "\n"] if 0 in lines else [box + "\n"]),
		]
		for line in range(1, max(lines, default=0) + 1):
			content += [copy.deepcopy(hover) if line in lines else "", "\n"]
		return content

	def box_beside(self, manual: Manual, name: str, craft: list[TextComponent], gap: int) -> list[TextComponent]:
		""" The item's box drawn ``gap`` pixels left of a craft from :meth:`RecipeRenderer.render_main`, both centered together.

		The dialog centers every line on its own. Each line of the craft ends with a space moving the pen back by the box and the gap,
		which shifts the whole craft right by half of them.
		The box sits on the left of its first lines through spaces netting to zero.
		"""
		space = manual.glyphs.add_space
		width: int = BOX_ADVANCE + gap
		box, hover = self.box_glyph(manual, name)
		lines: list[int] = self.box_hover_lines()
		box_lines: dict[int, list[TextComponent]] = {
			line: [space(-width), copy.deepcopy(hover), space(gap - 1)] for line in lines
		}
		box_lines[0] = [space(-width), {**hover, "text": box}, space(gap)] if 0 in lines else [space(-width) + box + space(gap)]

		return [*craft[:2], *self.wrap_lines(craft[2:], lambda line: box_lines.get(line, []), space(-width))]

	def box_hover_lines(self) -> list[int]:
		""" The lines, counted from the box's own, that the box covers over half of, each one carrying the item's tooltip.

		>>> ItemPage(anchor="item:demo").box_hover_lines()
		[1, 2, 3, 4]
		>>> ItemPage(anchor="item:demo", box_offset=-9).box_hover_lines()
		[0, 1, 2, 3]
		"""
		top: int = LINE_BASELINE + self.box_offset
		return [
			line for line in range((top + BOX_HEIGHT) // LINE_HEIGHT + 1)
			if min(LINE_HEIGHT * (line + 1), top + BOX_HEIGHT) - max(LINE_HEIGHT * line, top) > LINE_HEIGHT / 2
		]

	@staticmethod
	def moved(manual: Manual, parts: list[TextComponent], offset: tuple[int, int]) -> list[TextComponent]:
		""" The parts moved right by ``offset[0]`` pixels and down by ``offset[1]`` pixels rounded to whole lines of text.

		The spaces opening and closing every line cancel out, so the dialog centers each line as before and the move stays exact.
		"""
		x, y = offset
		if x:
			space = manual.glyphs.add_space
			parts = ItemPage.wrap_lines(parts, lambda _line: [space(x)], space(-x))
		return ["\n" * round(y / LINE_HEIGHT), *parts] if y else parts

	@staticmethod
	def wrap_lines(parts: list[TextComponent], starts: Callable[[int], list[TextComponent]], end: str) -> list[TextComponent]:
		""" The parts with ``starts(n)`` opening their line ``n`` and ``end`` closing every line.

		>>> ItemPage.wrap_lines(["a\\nb", {"text": "c"}], lambda line: [f"<{line}"], ">")
		['<0', 'a', '>\\n', '<1', 'b', {'text': 'c'}, '>']
		"""
		content: list[TextComponent] = list(starts(0))
		line: int = 0
		for part in parts:
			pieces: list[TextComponent] = list(part.split("\n")) if isinstance(part, str) else [part]
			for index, piece in enumerate(pieces):
				if index > 0:
					line += 1
					content += [end + "\n", *starts(line)]
				if piece:
					content.append(piece)
		content.append(end)
		return content

	def box_glyph(self, manual: Manual, name: str) -> tuple[str, JsonDict]:
		""" The glyph of the item in its box, hanging below its line, and the blank component showing the item's tooltip over it. """
		box = manual.glyphs.allocate()
		manual.images.recipe_image(name, box, ascent=-self.box_offset)
		hover: JsonDict = manual.recipes.item_component(name)
		hover["text"] = NONE_FONT * 2
		return box, hover

	def craft_buttons(self, manual: Manual, name: str, obj: Item | None) -> list[WikiButtonRender]:
		""" The item's info buttons, its growing seed, consume effects and remainder buttons,
		then a button per craft, skipping a repeat of the previous result.
		"""
		buttons: list[WikiButtonRender] = self.wiki_info_buttons(obj)
		gs_button = manual.recipes.growing_seed_button(obj) if obj is not None else None
		buttons += [button for button in (gs_button, self.consume_effects_button(obj)) if button is not None]

		buttons += self.source_links(manual, obj)

		previous_result = None
		for idx, craft in enumerate(self.crafts):
			craft_for_check = convert_shapeless_to_shaped(craft) if craft["type"] == "crafting_shapeless" else craft
			current_result = craft_for_check.get("result")
			if current_result and current_result == previous_result and craft["type"] != "mining":
				continue
			previous_result = current_result
			buttons.append(manual.recipes.render_button(craft, name, idx))
		return buttons

	def source_links(self, manual: Manual, obj: Item | None) -> list[WikiButtonRender]:
		""" Buttons opening the pages of the items this one leaves once used, is left by, or is grown by. """
		links: list[tuple[str, str]] = [("Leaves once used", obj.remainder)] if obj is not None and obj.remainder else []
		for source_id, source in manual.definitions_as_objects.items():
			if source.remainder == self.item_id:
				links.append(("Left by", source_id))
			seed = source.growing_seed if isinstance(source, Block) else None
			if seed and not isinstance(seed.loots, str) and any(loot.id == self.item_id for loot in seed.loots):
				links.append(("Grown by", source_id))

		return [
			manual.recipes.link_button(item, craft_type="source_link", hover=[
				{"text": title, "color": "yellow"},
				{"text": f"\n{Ingr(item).to_name()}", "color": "gray"},
				{"text": "\nClick to open its page", "color": "dark_gray"},
			])
			for title, item in links
		]

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
	def consume_effects_button(obj: Item | None) -> WikiButtonRender | None:
		""" An info button listing the effects the `consumable` component applies, None when it applies none.

		>>> item = Item(id="manual_beer", components={"consumable": {"on_consume_effects": [
		...     {"type": "minecraft:apply_effects", "effects": [{"id": "minecraft:nausea", "duration": 600}]},
		... ]}})
		>>> ItemPage.consume_effects_button(item).hover[1]
		{'text': '\\n- Nausea (0:30)', 'color': 'gray'}
		"""
		consumable: JsonDict = obj.components.get("consumable", {}) if obj is not None else {}
		effects: list[JsonDict] = [
			effect for entry in consumable.get("on_consume_effects", [])
			if entry["type"] == "minecraft:apply_effects" for effect in entry["effects"]
		]
		if not effects:
			return None
		hover: list[TextComponent] = [{"text": "When consumed", "color": "yellow"}]
		for effect in effects:
			name: str = item_id_to_name(effect["id"].split(":")[-1])
			level: str = f" {effect['amplifier'] + 1}" if effect.get("amplifier") else ""
			minutes, seconds = divmod(effect.get("duration", 0) // 20, 60)
			hover.append({"text": f"\n- {name}{level} ({minutes}:{seconds:02})", "color": "gray"})
		return WikiButtonRender(glyph=WIKI_INFO_FONT, hover=hover, is_info=True)

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
		grid: list[TextComponent] = self.button_grid(buttons, layout, manual)
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

	def button_grid(self, buttons: list[WikiButtonRender], layout: ButtonLayout, manual: Manual) -> list[TextComponent]:
		""" The buttons laid out as one grid, or as two side by side with ``layout.side_grid``, moved by ``layout.offset``. """
		grid: list[TextComponent] = []
		if layout.side_grid is None:
			self.render_button_grid(grid, buttons, layout)
		else:
			grid = self.side_by_side_grid(buttons, layout.columns, layout.side_grid, manual)
		return self.moved(manual, grid, layout.offset)

	def render_button_grid(self, content: list[TextComponent], buttons: list[WikiButtonRender], layout: ButtonLayout) -> None:
		""" Lay buttons into a grid, duplicating each line for the 2-row hover trick (ported). """
		content.append("\n")
		columns = max(1, layout.columns)
		for i, button in enumerate(buttons):
			if i % columns == 0 and i != 0:
				self.duplicate_row(content, columns)
				content.append("\n")
			content.append(self.button_to_component(button))

		last: int = len(buttons) - 1
		if last % columns != 0 or last == 0:
			self.duplicate_row(content, last % columns + 1)

	def side_by_side_grid(self, buttons: list[WikiButtonRender], columns: int, side: SideGrid, manual: Manual) -> list[TextComponent]:
		""" The first ``side.count`` buttons in a grid left of the others, every line of both padded with blank slots.

		Each line holds both grids at their full width, then a space taking the pen back over all of it,
		so the dialog centers a line of no width and the block is centered on the page.
		"""
		left: list[list[TextComponent]] = self.grid_lines(buttons[:side.count], side.columns)
		right: list[list[TextComponent]] = self.grid_lines(buttons[side.count:], columns)
		left = [self.blank_line(side.columns)] * max(0, side.lines) + left
		right = [self.blank_line(columns)] * max(0, -side.lines) + right
		height: int = max(len(left), len(right))
		left += [self.blank_line(side.columns)] * (height - len(left))
		right += [self.blank_line(columns)] * (height - len(right))

		space = manual.glyphs.add_space
		width: int = SLOT_ADVANCE * (side.columns + columns) - 2 * SPACING_ADVANCE + side.gap
		start, end = space(-(width // 2)), space(width // 2 - width)
		content: list[TextComponent] = []
		for left_line, right_line in zip(left, right, strict=True):
			content += ["\n", start, *left_line, space(side.gap), *right_line, end]
		return content

	def grid_lines(self, buttons: list[WikiButtonRender], columns: int) -> list[list[TextComponent]]:
		""" Two lines per row of ``columns`` slots, the buttons then blank copies keeping their hovers.

		The copies make a button hover over its full height, as :meth:`duplicate_row` does for a single grid.
		"""
		lines: list[list[TextComponent]] = []
		for start in range(0, len(buttons), columns):
			row: list[JsonDict] = [self.button_to_component(button) for button in buttons[start:start + columns]]
			row += [{"text": BLANK_SLOT} for _ in range(columns - len(row))]
			copies: list[JsonDict] = [{**slot, "text": BLANK_SLOT} for slot in row]
			for line in (row, copies):
				line[-1] = {**line[-1], "text": line[-1]["text"].replace(VERY_SMALL_NONE_FONT, "")}
			lines += [list[TextComponent](row), list[TextComponent](copies)]
		return lines

	@staticmethod
	def blank_line(columns: int) -> list[TextComponent]:
		""" A line of ``columns`` empty slots, as wide as a full row of buttons. """
		return [BLANK_SLOT * (columns - 1) + WIKI_NONE_FONT]

	@staticmethod
	def duplicate_row(content: list[TextComponent], count: int) -> None:
		""" Close the row of the last ``count`` buttons: drop the spacer that would wrap it,
		then repeat it blank on a second line, keeping its hovers.
		"""
		last = cast(JsonDict, content[-1])
		last["text"] = last["text"].replace(VERY_SMALL_NONE_FONT, "")
		copies: list[JsonDict] = [cast(JsonDict, button).copy() for button in content[-count:]]
		for index, button in enumerate(copies):
			button["text"] = WIKI_NONE_FONT + VERY_SMALL_NONE_FONT * (2 if index != count - 1 else 0)
		content += ["\n", *copies]

