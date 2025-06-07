
# Imports
import hashlib
import json
import os
import shutil
import time
from collections.abc import Callable

import stouputils as stp
from beet import PackConfig, ProjectConfig, run_beet

from .datapack.basic_structure import main as basic_structure_main
from .datapack.custom_block_ticks import custom_blocks_ticks_and_second_functions
from .datapack.headers import main as headers_main
from .datapack.lang import main as lang_main
from .dependencies.main import OFFICIAL_LIBS, OFFICIAL_LIBS_PATH
from .dependencies.main import main as dependencies_main
from .resource_pack.check_unused_textures import main as check_unused_textures_main
from .utils.archive import make_archive
from .utils.io import (
	FILES_TO_WRITE,
	delete_files,
	delete_old_files,
	super_copy,
	super_merge_dict,
	write_all_files,
	write_file,
)
from .utils.weld import weld_datapack, weld_resource_pack

confff = []

def beet_pipeline(ctx):
	user_code, config = confff
	config["beet_ctx"] = ctx
	user_code(config)


def main(config: dict, user_code: Callable|None = None):
	print()

	# Copy original_icon.png to pack.png if it exists
	if config.get('assets_folder') and os.path.exists(f"{config['assets_folder']}/original_icon.png"):
		super_copy(f"{config['assets_folder']}/original_icon.png", f"{config['build_datapack']}/pack.png")
		super_copy(f"{config['assets_folder']}/original_icon.png", f"{config['build_resource_pack']}/pack.png")
	else:
		stp.warning("No 'original_icon.png' found in assets folder, no icon will be set")

	# For every file in the merge folder, copy it to the build folder (with append content)
	if config.get('merge_folder'):
		for root, _, files in os.walk(config['merge_folder']):
			for file in files:
				merge_path = stp.clean_path(f"{root}/{file}")
				build_path = merge_path.replace(config['merge_folder'], config['build_folder'])

				# Append content to the build file is any
				if FILES_TO_WRITE.get(build_path):

					# If file is not JSON format,
					if not file.endswith(".json") and not file.endswith(".mcmeta"):
						with stp.super_open(merge_path, "r") as f:
							write_file(build_path, f.read())

					else:
						# Load to two dictionnaries
						with stp.super_open(merge_path, "r") as f:
							merge_dict = json.load(f)
						build_dict = json.loads(FILES_TO_WRITE[build_path])

						# Write the merged dictionnaries to the build file
						merged_dict = super_merge_dict(build_dict, merge_dict)
						write_file(build_path, stp.super_json_dump(merged_dict), overwrite = True)
				else:
					# Get content of .mcfunction file to correctly append headers
					if file.endswith((".json",".mcfunction",".mcmeta")):
						try:
							with stp.super_open(merge_path, "r") as f:
								write_file(build_path, f.read())
						except Exception as e:
							stp.warning(f"Could not read '{merge_path}': {e}")

					# Else, just copy the file, such as pack.mcmeta, pack.png, ...
					else:
						super_copy(merge_path, build_path)
		pass

	# Delete resource_pack folder if no subfolder 'assets' is found
	if not os.path.exists(f"{config['build_resource_pack']}/assets"):
		delete_files(config['build_resource_pack'], clean_on_disk = True)

	# Run user code
	if user_code:
		merge_folder: str = config["merge_folder"]
		beet_config = ProjectConfig(
			id=config["namespace"],
			name=config["project_name"],
			description=config["description"],
			author=config["author"],
			version=config["version"],
			require=[
				"bolt",
				"mecha.contrib.relative_location",
				"mecha.contrib.nested_location"
			],
			output=config["build_folder"],
			data_pack = PackConfig(load=f"{merge_folder}/datapack"), # type: ignore
			resource_pack = PackConfig(load=f"{merge_folder}/resource_pack"), # type: ignore
			meta={
				"model_resolver": {"use_cache": True},
				"mecha": {"multiline": True, "match": [f"{config['namespace']}:**"]}
			},
			pipeline=["stewbeet.finalyze.beet_pipeline"]
		)

		start_time: float = time.perf_counter()
		confff.append(user_code)
		confff.append(config)
		with run_beet(config=beet_config, cache=True):
			pass
		total_time: float = time.perf_counter() - start_time
		stp.info(f"User code ran in {total_time:.5f}s")

	# Second and tick functions for custom blocks
	custom_blocks_ticks_and_second_functions(config)

	# Generate basic datapack structure (tick, tick_2, second, second_5, minute) if needed
	basic_structure_main(config)

	# Check for official libs uses
	dependencies_main(config)

	# Generate lang file
	if config.get("enable_translations") is True:
		lang_main(config)

	# Add a small header for each .mcfunction file
	headers_main(config)

	# Write every pending files and delete old ones
	write_all_files(verbose = 1)
	delete_old_files()

	# Check not used textures
	if config.get('textures_files'):
		check_unused_textures_main(config)


	# Generate zip files
	datapack_dest: list[str] = config['build_copy_destinations'][0] if config.get('build_copy_destinations') else []
	resourcepack_dest: list[str] = config['build_copy_destinations'][1] if config.get('build_copy_destinations') and len(config['build_copy_destinations']) > 1 else []
	if isinstance(datapack_dest, str):
		datapack_dest = [datapack_dest]
	if isinstance(resourcepack_dest, str):
		resourcepack_dest = [resourcepack_dest]
	datapack_dest = [x for x in datapack_dest if x != ""]
	resourcepack_dest = [x for x in resourcepack_dest if x != ""]
	processes = [
		(config['build_datapack'],			f"{config['build_folder']}/{config['project_name_simple']}_datapack",			datapack_dest),
		(config['build_resource_pack'],		f"{config['build_folder']}/{config['project_name_simple']}_resource_pack",		resourcepack_dest)
	]
	for source, destination, copy_destinations in processes:
		if os.path.exists(source):
			total_time: float = make_archive(source, destination, copy_destinations)
			rel_dest: str = stp.clean_path(os.path.relpath(destination, os.getcwd()))
			stp.debug(f"'./{rel_dest}.zip' file generated and copied to destinations in {total_time:.5f}s")

	# Copy datapack libraries
	try:
		# Copy lib folder
		if config.get("libs_folder"):
			for root, _, files in os.walk(config["libs_folder"] + "/datapack"):
				for file in files:
					if file.endswith(".zip"):
						for dest in datapack_dest:
							shutil.copy(stp.clean_path(f"{root}/{file}"), stp.clean_path(dest))

		# Copy official used libs
		for data in OFFICIAL_LIBS.values():
			if data["is_used"]:
				name: str = data["name"]
				for dest in datapack_dest:
					shutil.copy(f"{OFFICIAL_LIBS_PATH}/datapack/{name}.zip", dest)

	except OSError as e:
		stp.warning(f"Could not copy datapack libraries to {datapack_dest}: {e}")


	# If merge libs is enabled, use weld to generate datapack and resource pack with bundled libraries
	if config.get("merge_libs") is True:

		# Merge weld dp
		weld_dp: str = f"{config['build_folder']}/{config['project_name_simple']}_datapack_with_libs.zip"
		weld_dp_time: float = weld_datapack(config, weld_dp)

		# Merge weld rp and copy to resourcepack_dest if possible
		if os.path.exists(f"{config['build_resource_pack']}/pack.mcmeta"):
			weld_rp: str = f"{config['build_folder']}/{config['project_name_simple']}_resource_pack_with_libs.zip"
			weld_rp_time: float = weld_resource_pack(config, weld_rp)
			for dest in resourcepack_dest:
				try:
					shutil.copy(weld_rp, dest)
				except OSError as e:
					print(e)
					pass
		else:
			weld_rp_time: float = 0.0

		# Debug time taken
		total_time: float = weld_dp_time + weld_rp_time
		stp.info(f"Datapack and resource pack merged with bundled libraries in {total_time:.5f}s ({weld_dp_time:.5f}s + {weld_rp_time:.5f}s)")

	# Get SHA1 hash for each zip file in build folder
	sha1_hashes: dict[str, str] = {}
	for file in os.listdir(config['build_folder']):
		if file.endswith(".zip"):
			with open(f"{config['build_folder']}/{file}", "rb") as f:
				sha1_hashes[file] = hashlib.sha1(f.read()).hexdigest()
	with stp.super_open(f"{config['build_folder']}/sha1_hashes.json", "w") as f:
		f.write(stp.super_json_dump(sha1_hashes))


