
# Imports
import os
import time
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import stouputils as stp
from smithed.weld.toolchain.cli import weld

from ..dependencies.main import OFFICIAL_LIBS, OFFICIAL_LIBS_PATH


# Weld datapack
@stp.handle_error()
@stp.silent
def weld_datapack(config: dict, dest_path: str) -> float:
	""" Merge the datapack and libs into one file using Weld
	Args:
		dest_path (str): The path to the destination file
	Returns:
		float: The time it took to merge the datapack and libs
	"""
	start_time: float = time.perf_counter()

	# Get all paths to merge
	datapacks_to_merge = [
		f"{config['build_folder']}/{config['project_name_simple']}_datapack.zip"
	]
	if config.get("libs_folder", ""):
		datapacks_to_merge.append(config["libs_folder"] + "/datapack/*.zip")

	# Add the used official libs
	for lib in OFFICIAL_LIBS.values():
		if lib["is_used"]:
			name: str = lib["name"]
			path: str = f"{OFFICIAL_LIBS_PATH}/datapack/{name}.zip"
			if os.path.exists(path):
				datapacks_to_merge.append(path)

	# Weld all datapacks
	output_dir = os.path.dirname(dest_path)
	output = os.path.basename(dest_path.replace(".zip", "_temporary.zip"))
	weld(datapacks_to_merge, Path(output_dir), Path(output), log = "error")

	# Get the constant time for the archive
	constant_time: tuple = (2024, 1, 1, 0, 0, 0)	# default time: 2024-01-01 00:00:00
	mcmeta_path: str = f"{config['build_datapack']}/pack.mcmeta"
	if os.path.exists(mcmeta_path):

		# Get the pack folder (and the data and assets folders paths)
		pack_folder: str = os.path.dirname(mcmeta_path)
		data_folder: str = f"{pack_folder}/data"
		assets_folder: str = f"{pack_folder}/assets"

		# Get the time of the data or assets folder if it exists, else get the time of the pack.mcmeta file
		if os.path.exists(data_folder):
			time_float: float = os.path.getmtime(data_folder)
		elif os.path.exists(assets_folder):
			time_float: float = os.path.getmtime(assets_folder)
		else:
			time_float: float = os.path.getmtime(mcmeta_path)
		constant_time = time.localtime(time_float)[:6]

	# Make the new zip file with fixed pack.mcmeta and pack.png
	with ZipFile(dest_path.replace(".zip", "_temporary.zip"), "r") as temp_zip:
		# Open the final destination zip file for writing
		with ZipFile(dest_path, "w", compression=ZIP_DEFLATED) as zip:
			# Iterate through all files in the temporary zip, and exclude pack.mcmeta and pack.png
			for file in temp_zip.namelist():
				if file not in ["pack.mcmeta", "pack.png"]:
					info: ZipInfo = ZipInfo(file)
					info.compress_type = ZIP_DEFLATED
					info.date_time = constant_time
					zip.writestr(info, temp_zip.read(file))

			# Add the fixed pack.mcmeta to the final zip with constant_time
			info: ZipInfo = ZipInfo("pack.mcmeta")
			info.compress_type = ZIP_DEFLATED
			info.date_time = constant_time
			with open(mcmeta_path, "rb") as f:
				zip.writestr(info, f.read())

			# Check if pack.png exists and add it to the final zip if it does
			if os.path.exists(f"{config['build_datapack']}/pack.png"):
				pack_png_path = f"{config['build_datapack']}/pack.png"

				# Copy the file with the same timestamp as mcmeta
				info: ZipInfo = ZipInfo("pack.png")
				info.compress_type = ZIP_DEFLATED
				info.date_time = constant_time
				with open(pack_png_path, "rb") as f:
					zip.writestr(info, f.read())

	# Remove temp file
	os.remove(dest_path.replace(".zip","_temporary.zip"))

	# Return the time it took to merge the datapack and libs
	return time.perf_counter() - start_time

# Weld resource pack
@stp.handle_error()
@stp.silent
def weld_resource_pack(config: dict, dest_path: str) -> float:
	""" Merge the resource pack and libs into one file using Weld
	Args:
		dest_path (str): The path to the destination file
	Returns:
		float: The time it took to merge the resource pack and libs
	"""
	start_time: float = time.perf_counter()

	# Get all paths to merge
	resource_packs_to_merge = [
		f"{config['build_folder']}/{config['project_name_simple']}_resource_pack.zip"
	]
	if config.get("libs_folder", ""):
		resource_packs_to_merge.append(config["libs_folder"] + "/resource_pack/*.zip")

	# Add the used official libs
	for lib in OFFICIAL_LIBS.values():
		if lib["is_used"]:
			name: str = lib["name"]
			path: str = f"{OFFICIAL_LIBS_PATH}/resource_pack/{name}.zip"
			if os.path.exists(path):
				resource_packs_to_merge.append(path)

	# Weld all resource packs
	output_dir = os.path.dirname(dest_path)
	output = os.path.basename(dest_path.replace(".zip", "_temporary.zip"))
	weld(resource_packs_to_merge, Path(output_dir), Path(output), log = "error")

	# Get the constant time for the archive
	constant_time: tuple = (2024, 1, 1, 0, 0, 0)	# default time: 2024-01-01 00:00:00
	mcmeta_path: str = f"{config['build_resource_pack']}/pack.mcmeta"
	if os.path.exists(mcmeta_path):

		# Get the pack folder (and the data and assets folders paths)
		pack_folder: str = os.path.dirname(mcmeta_path)
		data_folder: str = f"{pack_folder}/data"
		assets_folder: str = f"{pack_folder}/assets"

		# Get the time of the data or assets folder if it exists, else get the time of the pack.mcmeta file
		if os.path.exists(data_folder):
			time_float: float = os.path.getmtime(data_folder)
		elif os.path.exists(assets_folder):
			time_float: float = os.path.getmtime(assets_folder)
		else:
			time_float: float = os.path.getmtime(mcmeta_path)
		constant_time = time.localtime(time_float)[:6]

	# Make the new zip file with fixed pack.mcmeta and pack.png
	with ZipFile(dest_path.replace(".zip", "_temporary.zip"), "r") as temp_zip:
		# Open the final destination zip file for writing
		with ZipFile(dest_path, "w", compression=ZIP_DEFLATED) as zip:
			# Iterate through all files in the temporary zip, and exclude pack.mcmeta and pack.png
			for file in temp_zip.namelist():
				if file not in ["pack.mcmeta", "pack.png"]:
					info: ZipInfo = ZipInfo(file)
					info.compress_type = ZIP_DEFLATED
					info.date_time = constant_time
					zip.writestr(info, temp_zip.read(file))

			# Add the fixed pack.mcmeta to the final zip with constant_time
			info: ZipInfo = ZipInfo("pack.mcmeta")
			info.compress_type = ZIP_DEFLATED
			info.date_time = constant_time
			with open(mcmeta_path, "rb") as f:
				zip.writestr(info, f.read())

			# Check if pack.png exists and add it to the final zip if it does
			if os.path.exists(f"{config['build_resource_pack']}/pack.png"):
				pack_png_path = f"{config['build_resource_pack']}/pack.png"

				# Copy the file with the same timestamp as mcmeta
				info: ZipInfo = ZipInfo("pack.png")
				info.compress_type = ZIP_DEFLATED
				info.date_time = constant_time
				with open(pack_png_path, "rb") as f:
					zip.writestr(info, f.read())

	# Remove temp file
	os.remove(dest_path.replace(".zip","_temporary.zip"))

	# Return the time it took to merge the resource pack and libs
	return time.perf_counter() - start_time

