
# Imports
import logging
import os
import sys
import time
from glob import glob
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import stouputils as stp
from beet import Context

from ...dependencies.download_manager import get_lib_paths
from ..archive import get_consistent_timestamp
from ..initialize.source_lore_font import find_pack_png


# Weld datapack
@stp.handle_error
def weld_datapack(ctx: Context, dest_path: str) -> float:
	""" Merge the datapack and libs into one file using Weld
	Args:
		ctx (Context): The beet context
		dest_path (str): The path to the destination file
	Returns:
		float: The time it took to merge the datapack and libs
	"""
	start_time: float = time.perf_counter()

	# Get configuration from context
	stewbeet_config = ctx.meta.get("stewbeet", {})
	libs_folder = stewbeet_config.get("libs_folder", "libs")
	project_name_simple = ctx.project_name.replace(" ", "")

	# Get all paths to merge
	datapacks_to_merge = [
		str(Path(str(ctx.output_directory)) / f"{project_name_simple}_datapack.zip")
	]
	if libs_folder and os.path.exists(libs_folder):
		datapacks_to_merge.append(f"{libs_folder}/datapack/*.zip")

	# Add the used official libs (downloaded dynamically)
	for dl in get_lib_paths(ctx):
		if dl.datapack_path:
			datapacks_to_merge.append(dl.datapack_path)
	datapacks_to_merge = [x for pack in datapacks_to_merge for x in glob(pack)]
	datapacks_to_merge.reverse()	# Reverse so the main pack is last (overwrites pack format)

	# Skip welding if there are less than 2 datapacks to merge
	if len(datapacks_to_merge) < 2:
		stp.warning(f"No datapacks or libs to merge for {dest_path}. Skipping weld.", file=sys.stdout)
		return time.perf_counter() - start_time

	# Weld all datapacks
	output_dir = os.path.dirname(dest_path)
	output = os.path.basename(dest_path.replace(".zip", "_temporary.zip"))
	try:
		from smithed.weld.toolchain.cli import weld  # pyright: ignore[reportMissingTypeStubs]
	except Exception as e:
		stp.error(f"Smithed Weld merging failed: {e}\nThe 'smithed' package is not yet up to date with Python 3.14, consider installing from this fork:\npip install git+https://github.com/Stoupy51/smithed-python.git")
		return time.perf_counter() - start_time
	# Weld logs failures through the "weld" logger instead of raising, so capture its (noisy)
	# output and only replay it when an error actually happens
	stp.silent(weld, mute_stderr=True, replay_on_error=True, error_log_level=logging.ERROR, watch_loggers=["weld"])(
		datapacks_to_merge, Path(output_dir), Path(output), log="error"
	)

	# Get the consistent timestamp
	constant_time = get_consistent_timestamp(ctx)

	# Make the new zip file with fixed pack.mcmeta and pack.png
	with ZipFile(dest_path.replace(".zip", "_temporary.zip"), "r") as temp_zip:

		# Open the final destination zip file for writing
		with ZipFile(dest_path, "w", compression=ZIP_DEFLATED, compresslevel=6) as zip:

			# Iterate through all files in the temporary zip, and exclude pack.mcmeta and pack.png
			for file in temp_zip.namelist():
				if file not in ["pack.mcmeta", "pack.png"]:
					info: ZipInfo = ZipInfo(file)
					info.compress_type = ZIP_DEFLATED
					info.date_time = constant_time
					zip.writestr(info, temp_zip.read(file))

			# Add the fixed pack.mcmeta to the final zip with constant_time
			if hasattr(ctx.data, 'mcmeta') and ctx.data.mcmeta:
				info: ZipInfo = ZipInfo("pack.mcmeta")
				info.compress_type = ZIP_DEFLATED
				info.date_time = constant_time
				zip.writestr(info, ctx.data.mcmeta.text.encode('utf-8'))

			# Check if pack.png exists and add it to the final zip if it does
			pack_png_path = find_pack_png()
			if pack_png_path:
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
@stp.handle_error
def weld_resource_pack(ctx: Context, dest_path: str) -> float:
	""" Merge the resource pack and libs into one file using Weld
	Args:
		ctx (Context): The beet context
		dest_path (str): The path to the destination file
	Returns:
		float: The time it took to merge the resource pack and libs
	"""
	start_time: float = time.perf_counter()

	# Get configuration from context
	stewbeet_config = ctx.meta.get("stewbeet", {})
	libs_folder = stewbeet_config.get("libs_folder", "libs")
	project_name_simple = ctx.project_name.replace(" ", "")

	# Get all paths to merge
	resource_packs_to_merge = [
		str(Path(str(ctx.output_directory)) / f"{project_name_simple}_resource_pack.zip")
	]
	if libs_folder and os.path.exists(libs_folder):
		resource_packs_to_merge.append(f"{libs_folder}/resource_pack/*.zip")

	# Add the used official libs (downloaded dynamically)
	for dl in get_lib_paths(ctx):
		if dl.resource_pack_path:
			resource_packs_to_merge.append(dl.resource_pack_path)
	resource_packs_to_merge = [x for pack in resource_packs_to_merge for x in glob(pack)]
	resource_packs_to_merge.reverse()	# Reverse so the main pack is last (overwrites pack format)

	# Skip welding if there are less than 2 resource packs to merge
	if len(resource_packs_to_merge) < 2:
		stp.warning(f"No resource packs or libs to merge for {dest_path}. Skipping weld.", file=sys.stdout)
		return time.perf_counter() - start_time

	# Weld all resource packs
	output_dir = os.path.dirname(dest_path)
	output = os.path.basename(dest_path.replace(".zip", "_temporary.zip"))
	try:
		from smithed.weld.toolchain.cli import weld  # pyright: ignore[reportMissingTypeStubs]
	except Exception as e:
		stp.error(f"Smithed Weld merging failed: {e}\nThe 'smithed' package is not yet up to date with Python 3.14, consider installing from this fork:\npip install git+https://github.com/Stoupy51/smithed-python.git")
		return time.perf_counter() - start_time
	# Weld logs failures through the "weld" logger instead of raising, so capture its (noisy)
	# output and only replay it when an error actually happens
	stp.silent(weld, mute_stderr=True, replay_on_error=True, error_log_level=logging.ERROR, watch_loggers=["weld"])(
		resource_packs_to_merge, Path(output_dir), Path(output), log="error"
	)

	# Get the consistent timestamp
	constant_time = get_consistent_timestamp(ctx)

	# Make the new zip file with fixed pack.mcmeta and pack.png
	with ZipFile(dest_path.replace(".zip", "_temporary.zip"), "r") as temp_zip:
		# Open the final destination zip file for writing
		with ZipFile(dest_path, "w", compression=ZIP_DEFLATED, compresslevel=6) as zip:
			# Iterate through all files in the temporary zip, and exclude pack.mcmeta and pack.png
			for file in temp_zip.namelist():
				if file not in ["pack.mcmeta", "pack.png"]:
					info: ZipInfo = ZipInfo(file)
					info.compress_type = ZIP_DEFLATED
					info.date_time = constant_time
					zip.writestr(info, temp_zip.read(file))

			# Add the fixed pack.mcmeta to the final zip with constant_time
			if hasattr(ctx.assets, 'mcmeta') and ctx.assets.mcmeta:
				info: ZipInfo = ZipInfo("pack.mcmeta")
				info.compress_type = ZIP_DEFLATED
				info.date_time = constant_time
				zip.writestr(info, ctx.assets.mcmeta.text.encode('utf-8'))

			# Check if pack.png exists and add it to the final zip if it does
			pack_png_path = find_pack_png()
			if pack_png_path:
				info: ZipInfo = ZipInfo("pack.png")
				info.compress_type = ZIP_DEFLATED
				info.date_time = constant_time
				with open(pack_png_path, "rb") as f:
					zip.writestr(info, f.read())

	# Remove temp file
	os.remove(dest_path.replace(".zip","_temporary.zip"))

	# Return the time it took to merge the resource pack and libs
	return time.perf_counter() - start_time

