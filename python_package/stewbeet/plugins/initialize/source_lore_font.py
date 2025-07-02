
# Imports
import os
from pathlib import Path

from beet import Font, Texture
from beet.core.utils import TextComponent
from PIL import Image
from stouputils.io import super_json_dump

from ...core import Mem


# Utility functions
def find_pack_png() -> str | None:
	"""Find pack.png file in common locations."""
	pack_icon: str = ""
	for path in ("src/pack.png", "assets/pack.png"):
		if os.path.exists(path):
			pack_icon = path
			break
	if not pack_icon:
		pack_icon = next(Path(".").glob("*pack.png"), None)
	if not pack_icon:
		return None  # If the pack.png does not exist, return None
	return pack_icon


# Main function to create the source lore font
def prepare_source_lore_font(source_lore: TextComponent) -> str:

	# If the source_lore has an ICON text component and pack_icon is present,
	if source_lore and any(isinstance(component, dict) and "ICON" == component.get("text") for component in source_lore):

		pack_icon = find_pack_png()
		if not pack_icon:
			return ""

		# Replace every ICON text component with the original icon
		for component in source_lore:
			if isinstance(component, dict) and component.get("text") == "ICON":
				component["text"] = "I"
				component["color"] = "white"
				component["italic"] = False
				component["font"] = f"{Mem.ctx.project_id}:icons"
		source_lore.insert(0, "")
		Mem.ctx.meta.stewbeet.source_lore = source_lore
		return pack_icon

	return ""

def create_source_lore_font(pack_icon: str) -> None:
	""" Create the source lore font using the provided pack icon. """

	# Create the font file
	Mem.ctx.assets[Mem.ctx.project_id].fonts["icons"] = Font(
		super_json_dump({"providers": [{"type": "bitmap","file": f"{Mem.ctx.project_id}:font/original_icon.png","ascent": 8,"height": 9,"chars": ["I"]}]})
	)

	# Copy the pack.png to the resource pack
	image: Image.Image = Image.open(pack_icon).convert("RGBA")
	if image.width > 256:
		image = image.resize((256, 256))
	Mem.ctx.assets[Mem.ctx.project_id].textures["font/original_icon"] = Texture(image)

def delete_source_lore_font() -> None:
	""" Delete the source lore font if it exists. """
	if Mem.ctx.assets[Mem.ctx.project_id].fonts.get("icons"):
		del Mem.ctx.assets[Mem.ctx.project_id].fonts["icons"]
	if Mem.ctx.assets[Mem.ctx.project_id].textures.get("font/original_icon"):
		del Mem.ctx.assets[Mem.ctx.project_id].textures["font/original_icon"]

