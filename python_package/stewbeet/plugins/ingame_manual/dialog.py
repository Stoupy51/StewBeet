"""
Handles generation of dialogs based of book content
"""
from beet import Dialog, DialogTag
from beet.core.utils import JsonDict, TextComponent

from ...core import Mem, set_json_encoder
from .shared_import import BOOK_FONT, NONE_FONT


# Utility Function
def change_page_to_show_dialog(element: TextComponent, ns: str) -> None:
	if isinstance(element, dict) and "click_event" in element and element["click_event"]["action"] == "change_page":
		change_page: int = element["click_event"]["page"]
		element["click_event"] = {"action": "show_dialog", "dialog": f"{ns}:manual/page_{change_page}"}
	elif isinstance(element, list):
		for sub_element in element:
			change_page_to_show_dialog(sub_element, ns)

# Function
def generate_dialogs(book_content: list[list[TextComponent]]) -> None:
	ns: str = Mem.ctx.project_id

	# Generate dialogs for each page
	dialog_ids: list[str] = []
	for page_index, page in enumerate(book_content):
		dialog_id: str = f"manual/page_{page_index + 1}"
		dialog_ids.append(f"{ns}:{dialog_id}")

		# Previous and next page indexes
		previous_index: int = page_index - 1 if page_index > 0 else 0
		next_index: int = page_index + 1 if page_index + 1 < len(book_content) else page_index
		previous_dialog_id: str = f"{ns}:manual/page_{previous_index + 1}"
		next_dialog_id: str = f"{ns}:manual/page_{next_index + 1}"

		# Get title
		title: TextComponent = page[1]
		if isinstance(title, dict):
			title = title.get("text", "").replace("\n", "")
		else:
			title = str(title).replace("\n", "")

		# Generate the new body content
		new_content: list[TextComponent] = [{"text":"","font": f"{ns}:manual", "color": "white", "shadow_color": [0]*4}]	# Initial font and color
		if len(page) > 2:
			page = page[2:]	# Remove first two elements

			# Modify click events to show dialog instead of changing page
			change_page_to_show_dialog(page, ns)

			# Add to new content
			new_content.extend(page)
		new_content.append("\n"*12)	# Padding at the end to avoid cutoff

		# Create dialog
		dialog: JsonDict = {
			"type": "minecraft:multi_action",
			"title": {"text": title, "underlined": True},
			"body": [
				{
					"type": "minecraft:plain_message",
					"contents": {"text": BOOK_FONT + NONE_FONT*3, "font": f"{ns}:manual", "color": "white"},
					"width": 400
				},
				{
					"type": "minecraft:plain_message",
					"contents": new_content,
					"width": 150
				}
			],
			"exit_action": {"label": "Done"},
			"actions": [
				{"label": "<-", "width": 25, "action": {"type": "minecraft:show_dialog","dialog": previous_dialog_id}},	# TODO: Trigger page change count
				{"label": "->", "width": 25, "action": {"type": "minecraft:show_dialog","dialog": next_dialog_id}},
			]
		}
		Mem.ctx.data[ns].dialogs[dialog_id] = set_json_encoder(Dialog(dialog), max_level=4)
	pass

	# Generate main dialog to open the manual
	Mem.ctx.data["minecraft"].dialogs_tags["quick_actions"] = set_json_encoder(
		DialogTag({"replace": False, "values": dialog_ids}), max_level=-1
	)

