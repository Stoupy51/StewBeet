
# Imports
import os
import time
from collections.abc import Callable

import stouputils as stp

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


# Main function imports
from .__memory__ import StewBeetCfg  # noqa: F401
from .compatibilities.main import main as compatibilities_main
from .datapack.main import main as datapack_main
from .datapack.recipes import main as recipes_main
from .debug_info import main as debug_info_main
from .enhance_config import main as enhance_config_main
from .finalyze import main as finalyze_main
from .initialize import main as initialize_main
from .manual.main import main as manual_main
from .resource_pack.main import main as resource_pack_main
from .verify_database import main as verify_database_main


# Functions
def basic_key_check(config: dict, key: str, value_type: type, hint: str, valid: bool) -> bool:
	bool_return = valid
	if config.get(key, None) is None:
		bool_return = stp.warning(f"Missing '{key}' key in config file\n ({hint})") or False
	elif not isinstance(config[key], value_type):
		bool_return = stp.warning(f"Invalid type for '{key}' key in config file, found {type(config[key])} instead of {value_type}\n ({hint})") or False
	return bool_return

def check_config_format(config: dict) -> bool:
	KNOWN_KEYS: list[str] = ["build_folder","author","project_name", "version", "namespace", "description", "ignore_unset", "merge_folder", "assets_folder", "libs_folder", "build_copy_destinations", "debug_mode", "database_debug", "cmd_cache", "enable_translations", "merge_libs", "dependencies", "source_lore", "has_manual", "manual_path", "manual_overrides", "manual_high_resolution", "cache_manual_assets", "cache_manual_pages", "manual_debug", "manual_name", "max_items_per_row", "max_rows_per_page", "opengl_resolution", "manual_first_page_text"]
	valid: bool = True
	valid = basic_key_check(config, "build_folder", str, "Folder where the final datapack and resource pack are built", valid)
	valid = basic_key_check(config, "author", str, "Author(s) name(s) displayed in pack.mcmeta, also used to add convention.debug tag to the players of the same name(s) <-- showing additionnal displays like datapack loading", valid)
	valid = basic_key_check(config, "project_name", str, "Name of the datapack, used for messages and items lore", valid)
	valid = basic_key_check(config, "version", str, "Datapack version in the following mandatory format: major.minor.patch, ex: 1.0.0 or 1.21.615", valid)
	valid = basic_key_check(config, "namespace", str, "Used to namespace functions, tags, etc. Should be the same you use in the merge folder.", valid)
	valid = basic_key_check(config, "description", str, "Pack description displayed in pack.mcmeta", valid)
	if config.get("ignore_unset", None) is True:
		return valid
	valid = basic_key_check(config, "merge_folder", str, "If a file exists in both merge and build folder, they will be merged. Otherwise, it's just copied.", valid)
	valid = basic_key_check(config, "assets_folder", str, "Folder containing the all assets (textures, sounds, ...) for the datapack", valid)
	valid = basic_key_check(config, "libs_folder", str, "The libraries are copied to the build destination, and merged with the datapack using Weld", valid)
	valid = basic_key_check(config, "build_copy_destinations", tuple, "Can be empty paths if you don't want to copy the generated files", valid)
	valid = basic_key_check(config, "debug_mode", bool, "Shows up grids in manual", valid)
	valid = basic_key_check(config, "database_debug", str, "Dump of the database for debugging purposes", valid)
	valid = basic_key_check(config, "enable_translations", bool, "Will convert all the text components to translate and generate a lang file (WARNING: The algorithm is pretty slow, so it's recommended to disable it when not needed)", valid)
	valid = basic_key_check(config, "merge_libs", bool, "Make new zip of merged libraries with the datapack and resource pack using Smithed Weld", valid)
	valid = basic_key_check(config, "dependencies", dict, "Automagically, the datapack will check for the presence of dependencies and their minimum required versions at runtime\nThe url is used when the dependency is not found to suggest where to get it\nThe version dict key contains the minimum required version of the dependency in [major, minor, patch] format\nThe main key is the dependency namespace to check for\nThe name can be whatever you want, it's just used in messages", valid)
	valid = basic_key_check(config, "source_lore", list, "Appended lore to any custom item, can be an empty string to disable", valid)
	has_manual: bool|None = config.get("has_manual", None)
	if has_manual is not None:
		valid = basic_key_check(config, "has_manual", bool, "Do the program generate a manual/guide? (WARNING: if an item is malformed in the database, the server log will be flooded on load by the manual hiding the malformed item)", True)
	if has_manual is True:
		valid = basic_key_check(config, "manual_path", str, "Cached manual assets", valid)
		valid = basic_key_check(config, "manual_overrides", str, "Path to a folder containing manual overrides to replace the default manual assets", valid)
		valid = basic_key_check(config, "manual_high_resolution", bool, "Enable the high resolution for the manual to increase the craft resolutions", valid)
		valid = basic_key_check(config, "cache_manual_assets", bool, "Caches the MC assets and the items renders for the manual (manual/items/*.png)", valid)
		valid = basic_key_check(config, "cache_manual_pages", bool, "Caches the content of the manual and the images (manual/pages/*.png)", valid)
		valid = basic_key_check(config, "manual_debug", str, "Dump of the manual for debugging purposes", valid)
		valid = basic_key_check(config, "manual_name", str, "Name of the manual, used for the title of the book and first page", valid)
		valid = basic_key_check(config, "max_items_per_row", int, "Max number of items per row in the manual, should not exceed 6", valid)
		valid = basic_key_check(config, "max_rows_per_page", int, "Max number of rows per page in the manual, should not exceed 6", valid)
		valid = basic_key_check(config, "opengl_resolution", int, "Resolution of the OpenGL renders used in the manual, best value is 256 <--- 256x256", valid)
		valid = basic_key_check(config, "manual_first_page_text", list, "Text for the first page of the manual", valid)
	if valid is True:
		for key in config.keys():
			if key not in KNOWN_KEYS:
				stp.warning(f"Unknown key '{key}' in config file, it might be a typo or been removed from the configuration")
	return valid is True


def build_process(config: dict, setup_database: Callable|None = None, setup_external_database: Callable|None = None, user_code: Callable|None = None):
	""" Main function of the datapack build process
	Args:
		config					(dict):				Configuration of the program, the program will check the config format with high precision
		setup_database			(Callable|None):	Function that will setup the database of the datapack items and blocks, again the program will check the format of the database
		setup_external_database	(Callable|None):	Function that will setup the external database (if you need an item in a craft), same format as first
		user_code				(Callable|None):	Function that will be called after the datapack has been generated, can be used to add custom code to generated some parts of the datapack
	"""
	# Enable colors in Windows 10 console
	os.system("color")

	# Check config format
	valid = check_config_format(config)
	if not valid:
		stp.error("Invalid config format, please check the documentation")

	# Enhance config dict
	config = enhance_config_main(config)

	# Get start time &
	START_TIME: float = time.perf_counter()
	stp.info("Starting build process...")

	# Try to build the datapack
	try:

		# Initialize build process
		initialize_main(config)

		# Generate items/blocks database and verify the format
		config["database"] = setup_database(config) if setup_database else {}
		config["external_database"] = setup_external_database(config) if setup_external_database else {}
		if config.get("database"):
			verify_database_main(config)

		# Prepare debug info
		debug_info_main(config)

		# Generate resource pack
		if config.get("assets_folder"):
			resource_pack_main(config)

		# Generate custom recipes if any
		if config.get("database"):
			recipes_main(config)

		# Generate manual
		if config.get("has_manual") is True:
			manual_main(config)

		# Generate datapack
		datapack_main(config)

		# Special compatibilities with featured datapacks
		compatibilities_main(config)

		# Finalyze build process
		finalyze_main(config, user_code)

		# Total time
		TOTAL_TIME: float = time.perf_counter() - START_TIME
		stp.info(f"Build finished in {TOTAL_TIME:.5f} seconds")

	# Catch any exception
	except Exception as e:

		# Write all files to debug
		from .utils.io import write_all_files
		write_all_files()

		# Re-raise the exception
		raise e

