"""Dialog generation (the only manual output in v2).

Each page already produces its own dialog body (see :mod:`~.pages.base`), so the
:class:`DialogEmitter` only wraps that body with the title (item sprite or text, taken from
the page) and the prev/home/next navigation row — there is no book->dialog conversion. The
page->item mapping comes from :class:`~.manual.Manual` pages. The manual is reachable through
the vanilla ``quick_actions`` dialog tag.
"""

# Imports
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from beet import Advancement, Dialog, DialogTag, Texture
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.typing import JsonDict

from ...core import Mem, set_json_encoder, text_component_to_str, write_function, write_load_file
from ...core.utils.text_component import item_id_to_text_component
from ..initialize.source_lore_font import find_pack_png
from .glyphs import BOOK_FONT, HOME_FONT, NONE_FONT

if TYPE_CHECKING:
	from .manual import Manual


@dataclass(eq=False, slots=True)
class DialogEmitter:
	""" Builds one dialog per manual page plus the open-manual plumbing.

	``eq=False`` keeps identity semantics (the :class:`~.manual.Manual` reference would make
	field-based equality both meaningless and expensive).
	"""

	manual: Manual
	""" The manual whose rendered pages are emitted as dialogs. """

	def add_sprite(self, title: TextComponent, sprite: str) -> TextComponent:
		""" Wrap a title between two sprite icons (atlas-aware for pack format >= 93). """
		title = [
			"",
			{"sprite": sprite, "shadow_color": [0,0,0,0]},
			" ",
			{"text": text_component_to_str(title), "underlined": True},
			" ",
			{"sprite": sprite, "shadow_color": [0,0,0,0]},
		]
		if Mem.ctx.data.pack_format is not None:
			pack_format = cast("int | tuple[int, ...]", Mem.ctx.data.pack_format)
			pack_format = pack_format[0] if isinstance(pack_format, tuple) else pack_format
			if pack_format >= 93:
				title[1]["atlas"] = title[-1]["atlas"] = "minecraft:items"
		return title

	def get_atlas_title(self, item: str) -> TextComponent:
		""" Build a dialog title with the item's sprite if one is available, else its name. """
		ns: str = self.manual.config.project_id
		model = Mem.ctx.assets[ns].models.get(f"item/{item}")
		model_data: JsonDict = model.data if model else {}
		item_name: TextComponent = item_id_to_text_component(item)

		textures_values: list[str] = list(model_data.get("textures", {}).values())
		if len(textures_values) == 1 and "elements" not in model_data:
			sprite: str = textures_values[0]
			tns, path = sprite.split(":")
			texture_object = Mem.ctx.assets[tns].textures.get(path)
			if texture_object and texture_object.mcmeta:
				return self.add_sprite(item_name, sprite)

		supposed_path: str = f"{self.manual.config.cache_path}/items/{ns}/{item}.png"
		if os.path.exists(supposed_path):
			image: Image.Image = Image.open(supposed_path)
			if image.width > 16 or image.height > 16:
				image = image.resize((16, 16), Image.Resampling.LANCZOS)
			sprite_path: str = f"{ns}:item/dialog_sprite/{item}"
			Mem.ctx.assets.textures[sprite_path] = Texture(image)
			return self.add_sprite(item_name, sprite_path)
		return {**item_name, "underlined": True} if isinstance(item_name, dict) else {"text": str(item_name), "underlined": True}

	def emit(self) -> None:
		""" Generate per-page dialogs, the open-manual advancement, and the quick action. """
		manual = self.manual
		ns: str = manual.config.project_id
		pages_content = manual.pages_content

		dialog_ids: list[str] = []
		for page_index, page in enumerate(pages_content):
			dialog_id: str = f"manual/page_{page_index + 1}"
			dialog_ids.append(f"{ns}:{dialog_id}")

			prev_index: int = page_index - 1 if page_index > 0 else 0
			next_index: int = page_index + 1 if page_index + 1 < len(pages_content) else page_index
			prev_dialog_id: str = f"{ns}:manual/page_{prev_index + 1}"
			next_dialog_id: str = f"{ns}:manual/page_{next_index + 1}"

			# Title from the page itself: the item sprite for item pages, else its title text.
			page_obj = manual.pages[page_index] if page_index < len(manual.pages) else None
			if page_obj is not None and page_obj.item_id:
				title: TextComponent = self.get_atlas_title(page_obj.item_id)
			elif page_obj is not None and page_obj.title:
				title = {"text": page_obj.title, "underlined": True}
			else:
				title = ""

			# The page already produced its dialog body directly (no book->dialog conversion).
			new_content: list[TextComponent] = list(page)

			def count_breaklines(element: TextComponent) -> int:
				if isinstance(element, dict):
					return count_breaklines(element.get("text", ""))
				elif isinstance(element, list):
					return sum(count_breaklines(sub) for sub in element)
				return str(element).count("\n")
			nb_breaklines_to_add: int = max(0, 22 - count_breaklines(new_content))
			if nb_breaklines_to_add > 0:
				new_content.append("\n" * nb_breaklines_to_add)

			# Top navigation row: prev (left) | home (middle, -> first page) | next (right).
			# The home glyph shares NONE_FONT's advance so the prev/next layout stays put; it is
			# drawn on the first row and an invisible spacer on the second (extends the hit area).
			home_event: JsonDict = {
				"click_event": {"action": "show_dialog", "dialog": f"{ns}:manual/page_1"},
				"hover_event": {"action": "show_text", "value": [{"text": "Go to first page"}]},
			}
			prev_event: JsonDict = {
				"click_event": {"action": "show_dialog", "dialog": prev_dialog_id},
				"hover_event": {"action": "show_text", "value": [{"text": "Go to previous page"}, f" ({prev_index + 1})"]},
			}
			next_event: JsonDict = {
				"click_event": {"action": "show_dialog", "dialog": next_dialog_id},
				"hover_event": {"action": "show_text", "value": [{"text": "Go to next page"}, f" ({next_index + 1})"]},
			}
			# Book background & home button: the page's own override glyphs if set, else the shared ones.
			book_font: str = page_obj.book_font if page_obj is not None and page_obj.book_font else BOOK_FONT
			home_font: str = page_obj.home_font if page_obj is not None and page_obj.home_font else HOME_FONT
			nav_contents: list[TextComponent] = [{"text": book_font + NONE_FONT * 3, "font": f"{ns}:manual", "color": "white"}]
			# No home button on the first page (it IS the home page) or when the page opts out.
			hide_home: bool = page_index == 0 or (page_obj is not None and not page_obj.home_button)
			for row in range(2):
				nav_contents.append({"text": "\n" + NONE_FONT * 3, **prev_event})
				if hide_home:
					# Keep the spacing but drop the button
					nav_contents.append({"text": NONE_FONT, "font": f"{ns}:manual", "color": "white"})
				else:
					nav_contents.append({"text": (home_font if row == 0 else NONE_FONT), "font": f"{ns}:manual", "color": "white", **home_event})
				nav_contents.append({"text": NONE_FONT * 3, **next_event})

			dialog: JsonDict = {
				"type": "minecraft:notice",
				"title": title if title else {"text": ""},
				"body": [
					{"type": "minecraft:plain_message", "contents": nav_contents, "width": 400},
					{"type": "minecraft:plain_message", "contents": new_content, "width": 140},
				],
			}
			Mem.ctx.data[ns].dialogs[dialog_id] = set_json_encoder(Dialog(dialog), max_level=4)

		# Open-manual detection (mode 1, or whenever a manual item exists)
		if manual.config.use_dialog != 2 or "manual" in Mem.definitions:
			write_load_file(f"\n# Opening manual detection\nscoreboard objectives add {ns}.open_manual minecraft.used:minecraft.written_book\n", prepend=True)
			Mem.ctx.data[ns].advancements["technical/open_manual"] = set_json_encoder(Advancement({
				"criteria": {"requirement": {"trigger": "minecraft:tick", "conditions": {"player": [
					{"condition": "minecraft:entity_scores", "entity": "this", "scores": {f"{ns}.open_manual": {"min": 1}}}
				]}}},
				"rewards": {"function": f"{ns}:advancements/open_manual"},
			}), max_level=-1)
			write_function(f"{ns}:advancements/open_manual", f"""
# Revoke advancement and reset score
advancement revoke @s only {ns}:technical/open_manual
scoreboard players set @s {ns}.open_manual 0

# Show manual dialog if holding the manual
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{manual:true}}}}] run dialog show @s {ns}:manual/page_1
""")

		# Register the manual into the vanilla quick actions tag
		Mem.ctx.data["minecraft"].dialogs_tags["quick_actions"] = set_json_encoder(
			DialogTag({"replace": False, "values": [f"{ns}:all_manual"]})
		)

		# Main dialog list (with pack icon sprite)
		title2: TextComponent = {"text": f"{Mem.ctx.project_name} Manual"}
		pack_png: str | None = find_pack_png()
		if pack_png is not None:
			Mem.ctx.assets[ns].textures["item/dialog_sprite/pack_icon"] = Texture(source_path=pack_png)
			title2 = self.add_sprite(title2, f"{ns}:item/dialog_sprite/pack_icon")
		Mem.ctx.data[ns].dialogs["all_manual"] = set_json_encoder(Dialog({
			"type": "minecraft:dialog_list",
			"title": title2,
			"dialogs": dialog_ids,
			"exit_action": {"label": {"translate": "gui.back"}, "width": 200},
		}))

