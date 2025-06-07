
# Imports
import os

import stouputils as stp
from PIL import Image

from ..utils.io import write_file


# Utility functions
def main(config: dict) -> dict:
	namespace: str = config["namespace"]
	source_lore: list[dict|str] = config.get("source_lore", [])

	# If the source_lore has an ICON text component and original_icon is present,
	if source_lore and any(isinstance(component, dict) and "ICON" == component.get("text") for component in source_lore) and config.get("assets_folder"):
		original_icon: str = config["assets_folder"] + "/original_icon.png"
		if not os.path.exists(original_icon):
			return config

		# Create the font file
		write_file(
			f"{config['build_resource_pack']}/assets/{namespace}/font/icons.json",
			stp.super_json_dump({"providers": [{"type": "bitmap","file": f"{namespace}:font/original_icon.png","ascent": 8,"height": 9,"chars": ["I"]}]})
		)

		# Copy the original icon to the resource pack
		destination: str = f"{config['build_resource_pack']}/assets/{namespace}/textures/font/original_icon.png"
		os.makedirs(os.path.dirname(destination), exist_ok=True)
		image: Image.Image = Image.open(original_icon).convert("RGBA")
		if image.width > 256:
			image = image.resize((256, 256))
		image.save(destination)

		# Replace every ICON text component with the original icon
		for component in source_lore:
			if isinstance(component, dict) and component.get("text") == "ICON":
				component["text"] = "I"
				component["color"] = "white"
				component["italic"] = False
				component["font"] = f"{namespace}:icons"
		source_lore.insert(0, "")
		config["source_lore"] = source_lore

	return config

