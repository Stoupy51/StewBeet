
# Imports
import os

import stouputils as stp

from ..stewbeet.plugins.initialize.source_lore_font import main as source_lore_font


# Main function
def main(config: dict) -> dict:

	# Assets files
	if config.get('assets_folder'):
		config['assets_files'] = [stp.clean_path(f"{root}/{f}") for root, _, files in os.walk(config['assets_folder']) for f in files]
		textures: str = f"{config['assets_folder']}/textures"
		if os.path.exists(textures):
			config['textures_files'] = [path.split(f"{textures}/")[1] for path in config['assets_files'] if path.startswith(textures) and path.endswith(".png")]

	# Datapack related constants
	config['project_name_simple'] = "".join([c for c in config['project_name'] if c.isalnum()])		# Simplified version of the datapack name, used for paths

	# Technical constants
	config['build_datapack'] = f"{config['build_folder']}/datapack"										# Folder where the final datapack will be built
	config['build_resource_pack'] = f"{config['build_folder']}/resource_pack"							# Folder where the final resource pack will be built

	# If the source_lore has an ICON text component, make a font
	config = source_lore_font(config)

	return config

