
# Imports
import os
import shutil
import time

from beet import Context
from stouputils.decorators import handle_error, measure_time
from stouputils.io import relative_path
from stouputils.print import info, progress, warning

from ...core.constants import OFFICIAL_LIBS
from ...dependencies import OFFICIAL_LIBS_PATH


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.copy_to_destination'")
@handle_error(message="Error during 'stewbeet.plugins.copy_to_destination'")
def beet_default(ctx: Context) -> None:
	""" Copy destination plugin for StewBeet.
	Copies the datapack (not merged) and all libs zips to all datapack destinations.
	Copies the resource pack (merged if available, otherwise normal) to all resource pack destinations.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	assert ctx.output_directory, "Output directory must be specified in the project configuration."
	assert ctx.project_name, "Project name must be specified in the project configuration."

	# Get configuration data from context
	stewbeet_config = ctx.meta.get("stewbeet", {})
	build_copy_destinations = stewbeet_config.get("build_copy_destinations", {})

	if not build_copy_destinations:
		return

	datapack_destinations: list[str] = build_copy_destinations.get("datapack", [])
	resource_pack_destinations: list[str] = build_copy_destinations.get("resource_pack", [])

	if not datapack_destinations and not resource_pack_destinations:
		return
	project_name_simple = ctx.project_name.replace(" ", "")
	output_path = ctx.output_directory
	libs_folder = stewbeet_config.get("libs_folder", "libs")

	# Copy datapacks
	if datapack_destinations:
		_copy_datapacks(output_path, project_name_simple, libs_folder, datapack_destinations)

	# Copy resource packs
	if resource_pack_destinations:
		_copy_resource_packs(output_path, project_name_simple, resource_pack_destinations)

	# Copy official libs
	if datapack_destinations:
		_copy_official_libs(datapack_destinations)


def _copy_datapacks(output_path: str, project_name_simple: str, libs_folder: str, destinations: list[str]) -> None:
	""" Copy the main datapack and all library datapacks to specified destinations using file copying.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		libs_folder (str): The folder containing library files.
		destinations (list[str]): List of destination paths for datapacks.
	"""
	main_datapack = relative_path(f"{output_path}/{project_name_simple}_datapack.zip")

	if os.path.exists(main_datapack):
		for dest in destinations:
			dest_file = relative_path(f"{dest}/{os.path.basename(main_datapack)}")
			if _copy_with_retry(main_datapack, dest_file):
				info(f"Copied normal datapack to: '{dest_file}'")

	# Copy all library datapacks
	if libs_folder:
		libs_datapack_path = relative_path(f"{libs_folder}/datapack")
		if os.path.exists(libs_datapack_path):
			for lib_zip in os.listdir(libs_datapack_path):
				if lib_zip.endswith('.zip'):
					lib_zip_path = relative_path(f"{libs_datapack_path}/{lib_zip}")
					for dest in destinations:
						dest_file = relative_path(f"{dest}/{lib_zip}")
						if _copy_with_retry(lib_zip_path, dest_file):
							info(f"Copied library datapack to: '{dest_file}'")


def _copy_resource_packs(output_path: str, project_name_simple: str, destinations: list[str]) -> None:
	""" Copy the resource pack (merged if available, otherwise normal) to specified destinations using file copying.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		destinations (list[str]): List of destination paths for resource packs.
	"""
	merged_resource_pack: str = relative_path(f"{output_path}/{project_name_simple}_resource_pack_with_libs.zip")
	normal_resource_pack: str = relative_path(f"{output_path}/{project_name_simple}_resource_pack.zip")

	# Choose which resource pack to copy (merged takes priority)
	resource_pack_to_copy: str = merged_resource_pack if os.path.exists(merged_resource_pack) else normal_resource_pack

	if os.path.exists(resource_pack_to_copy):
		for dest in destinations:
			# Use original name (without _with_libs suffix) for the destination
			with_libs = "_with_libs" if resource_pack_to_copy == merged_resource_pack else ""
			dest_name = f"{project_name_simple}_resource_pack{with_libs}.zip"
			dest_file = relative_path(f"{dest}/{dest_name}")
			if _copy_with_retry(resource_pack_to_copy, dest_file):
				pack_type = "merged" if resource_pack_to_copy == merged_resource_pack else "normal"
				info(f"Copied {pack_type} resource pack to: '{dest_file}'")


def _copy_official_libs(datapack_destinations: list[str]) -> None:
	""" Copy official libraries to specified destinations using file copying.

	Args:
		datapack_destinations (list[str]): List of destination paths for datapacks.
	"""
	if not os.path.exists(OFFICIAL_LIBS_PATH):
		return

	# Copy official datapack libs
	if datapack_destinations:
		official_datapack_path = relative_path(f"{OFFICIAL_LIBS_PATH}/datapack")
		if os.path.exists(official_datapack_path):
			for lib in OFFICIAL_LIBS.values():
				if not lib.get("is_used", False):
					continue
				lib_name = lib["name"]
				lib_zip = f"{lib_name}.zip"
				lib_zip_path = relative_path(f"{official_datapack_path}/{lib_zip}")
				if os.path.exists(lib_zip_path):
					for dest in datapack_destinations:
						dest_file = relative_path(f"{dest}/{lib_zip}")
						if _copy_with_retry(lib_zip_path, dest_file):
							info(f"Copied official library to: '{dest_file}'")


def _copy_with_retry(src: str, dst: str, max_retries: int = 10, delay: float = 1.0) -> bool:
	""" Copy a file with retry logic to handle permission errors.

	Args:
		src (str): Source file path.
		dst (str): Destination file path.
		max_retries (int): Maximum number of retry attempts.
		delay (float): Delay in seconds between retries.
	Returns:
		bool: True if the copy was successful, False if it failed after all retries.
	"""
	# Delete the destination file if it exists (optional)
	if os.path.exists(dst):
		try:
			os.remove(dst)
		except PermissionError:
			pass

	# Ensure the destination directory exists
	dest_dir = os.path.dirname(dst)
	if not os.path.exists(dest_dir):
		warning(f"Destination directory '{dest_dir}' does not exist. Cannot copy file '{src}'.")
		return False

	# Attempt to copy the file with retries
	for attempt in range(max_retries):
		try:
			shutil.copy(src, dst)
			return True
		except PermissionError as e:
			if attempt == max_retries - 1:
				raise e
			warning(f"Failed to copy '{src}' the destinations ({e.__class__.__name__}). Retrying in {delay} seconds...")
			time.sleep(delay)
	return False  # If all retries failed, return False

