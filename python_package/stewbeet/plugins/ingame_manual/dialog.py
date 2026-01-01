"""
Handles generation of dialogs based of book content
"""
import os
from typing import cast

from beet import Advancement, Dialog, DialogTag, Model, Texture
from beet.core.utils import JsonDict, TextComponent
from PIL import Image

from stewbeet.core.utils.text_component import item_id_to_text_component

from ...core import Mem, set_json_encoder, text_component_to_str, write_function, write_load_file
from ..initialize.source_lore_font import find_pack_png
from .shared_import import BOOK_FONT, NONE_FONT, SharedMemory, get_item_from_page


# Utility Function
def change_page_to_show_dialog(element: TextComponent, ns: str) -> None:
	if isinstance(element, dict) and "click_event" in element and element["click_event"]["action"] == "change_page":
		change_page: int = element["click_event"]["page"]
		element["click_event"] = {"action": "show_dialog", "dialog": f"{ns}:manual/page_{change_page}"}
	elif isinstance(element, list):
		for sub_element in element:
			change_page_to_show_dialog(sub_element, ns)

def add_sprite(title: TextComponent, sprite: str) -> TextComponent:
	""" Add a sprite to a title with consideration for pack format

	Args:
		title (TextComponent): The title text
		sprite (str): The sprite to add
	Returns:
		TextComponent: The title with sprite
	"""
	title = [
		"",
		{"sprite":sprite,"shadow_color": [0]*4},
		" ",
		{"text":text_component_to_str(title),"underlined": True},
		" ",
		{"sprite":sprite,"shadow_color": [0]*4}
	]
	if Mem.ctx.data.pack_format is not None:
		pack_format = cast(int | tuple[int, ...], Mem.ctx.data.pack_format)
		pack_format = pack_format[0] if isinstance(pack_format, tuple) else pack_format
		if pack_format >= 93:
			title[1]["atlas"] = title[-1]["atlas"] = "minecraft:items"
	return title

def get_atlas_title(item: str, title: TextComponent) -> TextComponent:
	""" Get a title with an atlas sprite if possible

	Args:
		item (str): The item id
		title (TextComponent): The title text
	Returns:
		TextComponent: The title with atlas sprite (or original title if no sprite found)
	"""
	ns: str = Mem.ctx.project_id

	# Get model data & item name
	model: Model | None = Mem.ctx.assets[ns].models.get(f"item/{item}")
	model_data: JsonDict = model.data if model else {}
	item_name: TextComponent = item_id_to_text_component(item)

	# If one texture, and animated, and no elements mapping, use that animated texture
	textures_values: list[str] = list(model_data.get("textures", {}).values())
	if len(textures_values) == 1 and "elements" not in model_data:
		# Check for animated texture
		sprite: str = textures_values[0]
		ns, path = sprite.split(":")
		texture_object: Texture | None = Mem.ctx.assets[ns].textures.get(path)
		if texture_object and texture_object.mcmeta:
			return add_sprite(item_name, sprite)

	# Else, if the item is in the manual_cache textures, use that texture
	supposed_path: str = f"{SharedMemory.cache_path}/items/{ns}/{item}.png"
	if os.path.exists(supposed_path):
		# Load the image and downscale it to 16x16 if needed
		image: Image.Image = Image.open(supposed_path)
		if image.width > 16 or image.height > 16:
			image = image.resize((16, 16), Image.Resampling.LANCZOS)
		sprite_path: str = f"{ns}:item/dialog_sprite/{item}"
		Mem.ctx.assets.textures[sprite_path] = Texture(image)
		return add_sprite(item_name, sprite_path)

	# Else, return original title
	return text_component_to_str(title)


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
		supposed_item: str = get_item_from_page(page_index + 1)
		if supposed_item != "":
			title = get_atlas_title(supposed_item, title)
		else:
			title = text_component_to_str(title).replace("\n", "")
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
		Mem.ctx.data[ns].advancements["technical/open_manual"] = set_json_encoder(Advancement({
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
advancement revoke @s only {ns}:technical/open_manual
scoreboard players set @s {ns}.open_manual 0

# Show manual dialog if holding the manual
execute if items entity @s weapon.* *[custom_data~{{{ns}:{{manual:true}}}}] run dialog show @s {ns}:manual/page_1
""")

	## Generate main dialog to open the manual
	# Add to quick actions tag
	Mem.ctx.data["minecraft"].dialogs_tags["quick_actions"] = set_json_encoder(
		DialogTag({"replace": False, "values": [f"{ns}:all_manual"]})
	)

	# Generate a sprite with the pack icon
	title: TextComponent = {"text": f"{Mem.ctx.project_name} Manual"}
	pack_png: str | None = find_pack_png()
	if pack_png is not None:
		Mem.ctx.assets[ns].textures["item/dialog_sprite/pack_icon"] = Texture(source_path=pack_png)
		title = add_sprite(title, f"{ns}:item/dialog_sprite/pack_icon")

	# Create main manual dialog
	Mem.ctx.data[ns].dialogs["all_manual"] = set_json_encoder(Dialog({
		"type": "minecraft:dialog_list",
		"title": title,
		"dialogs": dialog_ids,
		"exit_action": {"label": {"translate": "gui.back"}, "width": 200}
	}))

