
# Imports
import os
import shutil
import time
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import stouputils as stp

from .io import FILES_TO_WRITE


# Function that makes an archive with consistency (same zip file each time)
def make_archive(source: str, destination: str, copy_destinations: list[str] | None = None) -> float:
	""" Make an archive with consistency.
	Creates a zip archive from a source directory, ensuring consistent file timestamps and contents.
	Uses FILES_TO_WRITE to track known files and maintain consistency between builds.

	Args:
		source              (str):              Source directory to archive
		destination         (str):              Path where the zip file will be created
		copy_destinations   (list[str] | None): Optional list of additional paths to copy the archive to
	Returns:
		float:              Time taken to create the archive in seconds
	"""
	if copy_destinations is None:
		copy_destinations = []
	start_time: float = time.perf_counter()

	# Fix copy_destinations type if needed
	if copy_destinations and isinstance(copy_destinations, str):
		copy_destinations = [copy_destinations]

	# Get all files that are not in FILES_TO_WRITE
	not_known_files: list[str] = []
	for root, _, files in os.walk(source):
		for file in files:
			file_path: str = stp.clean_path(os.path.join(root, file))
			if file_path not in FILES_TO_WRITE:
				not_known_files.append(file_path)

	# Get the constant time for the archive
	constant_time: tuple[int, ...] = (2024, 1, 1, 0, 0, 0)	# default time: 2024-01-01 00:00:00
	for file in FILES_TO_WRITE:
		if file.endswith("pack.mcmeta"):

			# Get the pack folder (and the data and assets folders paths)
			pack_folder: str = os.path.dirname(file)
			data_folder: str = f"{pack_folder}/data"
			assets_folder: str = f"{pack_folder}/assets"

			# Get the time of the data or assets folder if it exists, else get the time of the pack.mcmeta file
			if os.path.exists(data_folder):
				time_float: float = os.path.getmtime(data_folder)
			elif os.path.exists(assets_folder):
				time_float: float = os.path.getmtime(assets_folder)
			else:
				time_float: float = os.path.getmtime(file)
			constant_time = time.localtime(time_float)[:6]
			break

	# Create the archive
	destination = destination if ".zip" in destination else destination + ".zip"

	def process_file(file: str, is_known: bool) -> tuple[ZipInfo, bytes] | None:
		""" Process a single file for the archive.

		Args:
			file (str): Path to the file to process.
			is_known (bool): Whether the file is in FILES_TO_WRITE.

		Returns:
			tuple[ZipInfo, bytes] | None: Tuple containing the ZipInfo and file contents, or None if file should be skipped.
		"""
		if source not in file:
			return None

		base_path: str = file.replace(source, "").strip("/")
		info: ZipInfo = ZipInfo(base_path)
		info.compress_type = ZIP_DEFLATED
		info.date_time = constant_time

		if is_known:
			file_content = FILES_TO_WRITE[file]
			content: bytes = file_content.encode() if isinstance(file_content, str) else file_content
		else:
			with open(file, "rb") as f:
				content: bytes = f.read()

		return info, content

	# Prepare file list for processing
	file_list: list[tuple[str, bool]] = [(f, False) for f in not_known_files] + [(f, True) for f in FILES_TO_WRITE.keys()]

	# Process files in parallel
	results: list[tuple[ZipInfo, bytes] | None] = stp.multithreading(process_file, sorted(file_list), use_starmap=True, max_workers=min(32, len(file_list)))

	for retry in range(10):
		try:
			# Write results directly to zip file
			with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=6) as zip:
				for result in results:
					if result is not None:
						info, content = result
						zip.writestr(info, content)

			# Copy the archive to the destination(s)
			for dest_folder in copy_destinations:
				try:
					dest_folder = stp.clean_path(dest_folder)
					if dest_folder.endswith("/"):
						file_name = destination.split("/")[-1]
						shutil.copy(stp.clean_path(destination), f"{dest_folder}/{file_name}")

					# Else, it's not a folder but a file path
					else:
						shutil.copy(stp.clean_path(destination), dest_folder)
				except Exception as e:
					stp.warning(f"Unable to copy '{stp.clean_path(destination)}' to '{dest_folder}', reason: {e}")

			# Return the time taken to archive the source folder
			return time.perf_counter() - start_time

		# If OSError, means another program tried to read the zip file.
		# Therefore, try 10 times before stopping and send warning
		except OSError:
			stp.warning(f"Unable to archive '{source}' due to file being locked by another process. Retry {retry+1}/10...")
			time.sleep(1.0)  # Wait a bit before retrying

	# Final error message
	stp.error(f"Failed to archive '{source}' after 10 attempts due to file being locked by another process")
	return 0.0

