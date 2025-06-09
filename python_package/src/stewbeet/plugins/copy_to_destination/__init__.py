
# Imports
import os

from beet import Context
from stouputils.decorators import measure_time
from stouputils.io import relative_path
from stouputils.print import info, progress

from ...core.constants import OFFICIAL_LIBS
from ...dependencies import OFFICIAL_LIBS_PATH


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.copy_to_destination'")
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
	""" Copy the main datapack and all library datapacks to specified destinations using symlinks.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		libs_folder (str): The folder containing library files.
		destinations (list[str]): List of destination paths for datapacks.
	"""
	main_datapack = relative_path(f"{output_path}/{project_name_simple}_datapack.zip")

	if os.path.exists(main_datapack):
		for dest in destinations:
			os.makedirs(dest, exist_ok=True)
			dest_file = relative_path(f"{dest}/{os.path.basename(main_datapack)}")
			# Remove existing symlink/file if it exists
			if os.path.exists(dest_file) or os.path.islink(dest_file):
				os.unlink(dest_file)
			os.symlink(os.path.abspath(main_datapack), dest_file)
			info(f"Symlinked normal datapack to: '{dest_file}'")

	# Copy all library datapacks
	if libs_folder:
		libs_datapack_path = relative_path(f"{libs_folder}/datapack")
		if os.path.exists(libs_datapack_path):
			for lib_zip in os.listdir(libs_datapack_path):
				if lib_zip.endswith('.zip'):
					lib_zip_path = relative_path(f"{libs_datapack_path}/{lib_zip}")
					for dest in destinations:
						os.makedirs(dest, exist_ok=True)
						dest_file = relative_path(f"{dest}/{lib_zip}")
						# Remove existing symlink/file if it exists
						if os.path.exists(dest_file) or os.path.islink(dest_file):
							os.unlink(dest_file)
						os.symlink(os.path.abspath(lib_zip_path), dest_file)
						info(f"Symlinked library datapack to: '{dest_file}'")


def _copy_resource_packs(output_path: str, project_name_simple: str, destinations: list[str]) -> None:
	""" Copy the resource pack (merged if available, otherwise normal) to specified destinations using symlinks.

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
			os.makedirs(dest, exist_ok=True)
			# Use original name (without _with_libs suffix) for the destination
			dest_name = f"{project_name_simple}_resource_pack.zip"
			dest_file = relative_path(f"{dest}/{dest_name}")
			# Remove existing symlink/file if it exists
			if os.path.exists(dest_file) or os.path.islink(dest_file):
				os.unlink(dest_file)
			os.symlink(os.path.abspath(resource_pack_to_copy), dest_file)
			pack_type = "merged" if resource_pack_to_copy == merged_resource_pack else "normal"
			info(f"Symlinked {pack_type} resource pack to: '{dest_file}'")


def _copy_official_libs(datapack_destinations: list[str]) -> None:
	""" Copy official libraries to specified destinations using symlinks.

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
						os.makedirs(dest, exist_ok=True)
						dest_file = relative_path(f"{dest}/{lib_zip}")
						# Remove existing symlink/file if it exists
						if os.path.exists(dest_file) or os.path.islink(dest_file):
							os.unlink(dest_file)
						os.symlink(os.path.abspath(lib_zip_path), dest_file)

