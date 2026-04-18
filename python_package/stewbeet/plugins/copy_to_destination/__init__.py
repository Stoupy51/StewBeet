
# Imports
import os
import shutil
import urllib.parse

import fsspec  # type: ignore
import stouputils as stp
from beet import Context

from ...dependencies.download_manager import get_lib_paths


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.copy_to_destination'")
@stp.handle_error(message="Error during 'stewbeet.plugins.copy_to_destination'")
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
	output_path: str = str(ctx.output_directory)
	libs_folder: str = str(stewbeet_config.get("libs_folder", "libs"))

	# Copy datapacks
	if datapack_destinations:
		_copy_datapacks(output_path, project_name_simple, libs_folder, datapack_destinations)

	# Copy resource packs
	if resource_pack_destinations:
		_copy_resource_packs(output_path, project_name_simple, resource_pack_destinations)

	# Copy official libs
	if datapack_destinations:
		_copy_official_libs(ctx, datapack_destinations)

def _is_sftp_path(path: str) -> bool:
	return path.startswith("sftp://")

def _copy_datapacks(output_path: str, project_name_simple: str, libs_folder: str, destinations: list[str]) -> None:
	""" Copy the main datapack and all library datapacks to specified destinations using file copying.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		libs_folder (str): The folder containing library files.
		destinations (list[str]): List of destination paths for datapacks.
	"""
	any_copied: bool = False
	main_datapack = f"{output_path}/{project_name_simple}_datapack.zip"

	if os.path.exists(main_datapack):
		for dest in destinations:
			dest_file = f"{dest}/{os.path.basename(main_datapack)}"
			if _copy_with_retry(main_datapack, dest_file):
				any_copied = True

	# Copy all library datapacks
	if libs_folder:
		libs_datapack_path = f"{libs_folder}/datapack"
		if os.path.exists(libs_datapack_path):
			for lib_zip in os.listdir(libs_datapack_path):
				if lib_zip.endswith('.zip'):
					lib_zip_path = f"{libs_datapack_path}/{lib_zip}"
					for dest in destinations:
						dest_file = f"{dest}/{lib_zip}"
						if _copy_with_retry(lib_zip_path, dest_file):
							any_copied = True

	if any_copied:
		stp.info(f"Copied datapacks to destinations: {', '.join(stp.relative_path(x) for x in destinations)}")


def _copy_resource_packs(output_path: str, project_name_simple: str, destinations: list[str]) -> None:
	""" Copy the resource pack (merged if available, otherwise normal) to specified destinations using file copying.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		destinations (list[str]): List of destination paths for resource packs.
	"""
	any_copied: bool = False
	merged_resource_pack: str = f"{output_path}/{project_name_simple}_resource_pack_with_libs.zip"
	normal_resource_pack: str = f"{output_path}/{project_name_simple}_resource_pack.zip"

	# Choose which resource pack to copy (merged takes priority)
	resource_pack_to_copy: str = merged_resource_pack if os.path.exists(merged_resource_pack) else normal_resource_pack

	if os.path.exists(resource_pack_to_copy):
		pack_type = "merged" if resource_pack_to_copy == merged_resource_pack else "normal"
		for dest in destinations:
			# Use original name (without _with_libs suffix) for the destination
			with_libs = "_with_libs" if resource_pack_to_copy == merged_resource_pack else ""
			dest_name = f"{project_name_simple}_resource_pack{with_libs}.zip"
			dest_file = f"{dest}/{dest_name}"
			if _copy_with_retry(resource_pack_to_copy, dest_file):
				any_copied = True

	if any_copied:
		pack_type = "merged" if resource_pack_to_copy == merged_resource_pack else "normal"
		stp.info(f"Copied {pack_type} resource pack to destinations: {', '.join(stp.relative_path(x) for x in destinations)}")


def _copy_official_libs(ctx: Context, datapack_destinations: list[str]) -> None:
	""" Copy official libraries to specified destinations using file copying.

	Args:
		ctx (Context): The beet context (used to resolve download paths).
		datapack_destinations (list[str]): List of destination paths for datapacks.
	"""
	any_copied: bool = False
	for dl in get_lib_paths(ctx):
		if not dl.datapack_path or not os.path.exists(dl.datapack_path):
			continue
		for dest in datapack_destinations:
			dest_file = f"{dest}/{dl.name}.zip"
			if _copy_with_retry(dl.datapack_path, dest_file):
				any_copied = True
	if any_copied:
		stp.info(f"Copied official libraries to datapack destinations: {', '.join(stp.relative_path(x) for x in datapack_destinations)}")

def _copy_to_sftp(src: str, dst: str) -> bool:
	""" Copy a local file to an SFTP destination URL.

	Args:
		src (str): Local source file path.
		dst (str): SFTP destination URL (sftp://user:pass@host/path).
	Returns:
		bool: True if successful.
	"""
	parsed = urllib.parse.urlparse(dst)
	password: str | None = parsed.password

	# Try to find password in credentials file
	if not password:
		creds_path = stp.clean_path("~/stewbeet/credentials.yml")
		if os.path.exists(creds_path):
			import yaml
			with open(creds_path) as f:
				creds = yaml.safe_load(f)
			password = creds.get("sftp", {}).get(parsed.netloc, {}).get("password")

	# Create SFTP filesystem
	fs = fsspec.filesystem( # type: ignore
		"sftp",
		host=parsed.hostname,
		username=parsed.username,
		password=password,
		port=parsed.port or 22,
	)

	remote_dir: str = os.path.dirname(parsed.path)
	if not fs.exists(remote_dir):
		stp.warning(f"Remote directory '{remote_dir}' does not exist. Cannot copy file '{src}'.")
		return False

	fs.put(src, parsed.path)
	return True

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
	# Cas SFTP
	if _is_sftp_path(dst):
		return _copy_to_sftp(src, dst)

	# Delete the destination file if it exists (optional)
	if os.path.exists(dst):
		try:
			os.remove(dst)
		except PermissionError:
			pass

	# Ensure the destination directory exists
	dest_dir = os.path.dirname(dst)
	if not os.path.exists(dest_dir):
		stp.warning(f"Destination directory '{dest_dir}' does not exist. Cannot copy file '{src}'.")
		return False

	# Attempt to copy the file with retries
	stp.retry(shutil.copy, exceptions=PermissionError, max_attempts=max_retries, delay=delay)(src, dst)
	return False  # If all retries failed, return False

