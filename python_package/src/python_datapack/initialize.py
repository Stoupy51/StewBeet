
# Imports
import os
import shutil

import stouputils as stp

from ..stewbeet.core.constants import DATAPACK_FORMAT, RESOURCE_PACK_FORMAT
from .utils.io import read_initial_files, write_file


def main(config: dict):

	# Delete database_debug
	if config.get("database_debug"):
		shutil.rmtree(config["database_debug"], ignore_errors=True)

	# Read initial files in build folder
	read_initial_files([config["build_datapack"], config["build_resource_pack"]])

	# Setup pack.mcmeta for the datapack
	pack_mcmeta = {"pack":{"pack_format": DATAPACK_FORMAT, "description": config["description"]}, "id": config["namespace"]}
	write_file(f"{config['build_datapack']}/pack.mcmeta", stp.super_json_dump(pack_mcmeta))

	# Setup pack.mcmeta for the resource pack
	pack_mcmeta = {"pack":{"pack_format": RESOURCE_PACK_FORMAT, "description": config["description"]}, "id": config["namespace"]}
	write_file(f"{config['build_resource_pack']}/pack.mcmeta", stp.super_json_dump(pack_mcmeta))

	# Convert textures names if needed
	if config.get('textures_files'):
		REPLACEMENTS = {
			"_off": "",
			"_down": "_bottom",
			"_up": "_top",
			"_north": "_front",
			"_south": "_back",
			"_west": "_left",
			"_east": "_right",
		}
		for file in config['textures_files']:
			new_name = file.lower()
			for k, v in REPLACEMENTS.items():
				if k in file:
					new_name = new_name.replace(k, v)
			if new_name != file:
				os.rename(f"{config['assets_folder']}/textures/{file}", f"{config['assets_folder']}/textures/{new_name}")
				stp.info(f"Renamed {file} to {new_name}")
	pass

