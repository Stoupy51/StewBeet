"""
Handles generation of dialogs based of book content
"""
from beet import Advancement, Dialog, DialogTag
from beet.core.utils import JsonDict, TextComponent

from ...core import Mem, set_json_encoder, write_function, write_load_file
from .shared_import import BOOK_FONT, NONE_FONT, SharedMemory


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
		prev_index: int = page_index - 1 if page_index > 0 else 0
		next_index: int = page_index + 1 if page_index + 1 < len(book_content) else page_index
		prev_dialog_id: str = f"{ns}:manual/page_{prev_index + 1}"
		next_dialog_id: str = f"{ns}:manual/page_{next_index + 1}"

		# Get title
		title: TextComponent = page[1]
		if isinstance(title, dict):
			title = str(title.get("text", "")).replace("\n", "")
			supposed_item: str = title.replace(" ", "_").lower()
			if Mem.definitions.get(supposed_item, {}).get("item_model") is not None:
				model = Mem.ctx.assets[ns].models.get(f"item/{supposed_item}")
				if model is not None and supposed_item != "heavy_workbench":
					all_textures: set[str] = set(model.data.get("textures", {}).values())
					if len(all_textures) == 1:
						sprite: str = all_textures.pop()
						if Mem.ctx.assets.textures.get(sprite) is not None:
							title = [{"sprite":sprite,"shadow_color": [0]*4}," ",{"text":title,"underlined": True}," ",{"sprite":sprite}]
		else:
			title = str(title).replace("\n", "")
		if isinstance(title, str) and len(title.strip()) < 2:
			title = page[2]
			if isinstance(title, dict):
				title = str(title.get("text", "")).replace("\n", "")
			page = page[:1] + page[2:]  # Remove title from body if taken from body

		# Generate the new body content
		new_content: list[TextComponent] = [{"text":"","font": f"{ns}:manual", "color": "white", "shadow_color": [0]*4}]	# Initial font and color
		if len(page) > 2:
			page = page[2:]	# Remove first two elements

			# Modify click events to show dialog instead of changing page
			change_page_to_show_dialog(page, ns)

			# Add to new content
			new_content.extend(page)

		# Add padding to avoid texture cutoff
		def count_breaklines(element: TextComponent) -> int:
			if isinstance(element, dict):
				return count_breaklines(element.get("text", ""))
			elif isinstance(element, list):
				return sum(count_breaklines(sub_element) for sub_element in element)
			return str(element).count("\n")
		nb_breaklines_to_add: int = max(0, 25 - count_breaklines(new_content))
		if nb_breaklines_to_add > 0:
			new_content.append("\n"*nb_breaklines_to_add)

		# Create dialog
		dialog: JsonDict = {
			"type": "minecraft:notice",
			"title": {"text": title, "underlined": True} if isinstance(title, str) else title,
			"body": [
				{
					"type": "minecraft:plain_message",
					"contents": [
						{"text": BOOK_FONT + NONE_FONT*3, "font": f"{ns}:manual", "color": "white"},
						*(2 * [
							{"text": "\n" + NONE_FONT*3, "click_event": {"action": "show_dialog", "dialog": prev_dialog_id},
								"hover_event": {"action": "show_text", "value": [{"text": "Go to previous page"}, f" ({prev_index + 1})"]}},
							NONE_FONT,
							{"text": NONE_FONT*3, "click_event": {"action": "show_dialog", "dialog": next_dialog_id},
								"hover_event": {"action": "show_text", "value": [{"text": "Go to next page"}, f" ({next_index + 1})"]}}
						])
					],
					"width": 400
				},
				{
					"type": "minecraft:plain_message",
					"contents": new_content,
					"width": 140
				}
			],
		}
		Mem.ctx.data[ns].dialogs[dialog_id] = set_json_encoder(Dialog(dialog), max_level=4)
	pass

	# Generate an advancement detecting when the manual is opened
	if SharedMemory.use_dialog != 2:
		write_load_file(f"\n# Opening manual detection\nscoreboard objectives add {ns}.open_manual minecraft.used:minecraft.written_book\n", prepend=True)
		Mem.ctx.data[ns].advancements["open_manual"] = set_json_encoder(Advancement({
			"criteria": {
				"requirement": {
					"trigger": "minecraft:tick",
					"conditions": {
						"player": [
							{
								"condition": "minecraft:entity_scores",
								"entity": "this",
								"scores": {f"{ns}.open_manual": {"min": 1}}
							}
						]
					}
				}
			},
			"rewards": {
				"function": f"{ns}:advancements/open_manual"
			}
		}), max_level=-1)
		write_function(f"{ns}:advancements/open_manual", f"""
# Revoke advancement and reset score
advancement revoke @s only {ns}:open_manual
scoreboard players set @s {ns}.open_manual 0

# Show manual dialog if holding the manual
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{manual:true}}}}] run dialog show @s {ns}:manual/page_1
""")

	# Generate main dialog to open the manual
	Mem.ctx.data["minecraft"].dialogs_tags["quick_actions"] = set_json_encoder(
		DialogTag({"replace": False, "values": [f"{ns}:all_manual"]})
	)
	Mem.ctx.data[ns].dialogs["all_manual"] = set_json_encoder(Dialog({
		"type": "minecraft:dialog_list",
		"title": {"text": f"{Mem.ctx.project_name} Manual"},
		"dialogs": dialog_ids,
		"exit_action": {"label": {"translate": "gui.back"}, "width": 200}
	}))

