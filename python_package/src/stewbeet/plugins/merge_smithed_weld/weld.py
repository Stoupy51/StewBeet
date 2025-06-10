# Imports
import os
import time
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from beet import Context
from smithed.weld.toolchain.cli import weld
from stouputils.decorators import handle_error, silent

from ...core.constants import OFFICIAL_LIBS
from ...dependencies import OFFICIAL_LIBS_PATH
from ..archive import get_consistent_timestamp
from ..initialize.source_lore_font import find_pack_png


# Weld datapack
@handle_error
@silent
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
		str(Path(ctx.output_directory) / f"{project_name_simple}_datapack.zip")
	]
	if libs_folder:
		datapacks_to_merge.append(f"{libs_folder}/datapack/*.zip")

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
@handle_error
@silent
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
		str(Path(ctx.output_directory) / f"{project_name_simple}_resource_pack.zip")
	]
	if libs_folder:
		resource_packs_to_merge.append(f"{libs_folder}/resource_pack/*.zip")

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

