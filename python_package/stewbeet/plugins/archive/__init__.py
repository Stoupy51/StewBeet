
# Imports
import os
import time
import zipfile
from zipfile import ZipInfo

from beet import Context, DataPack, ResourcePack
from stouputils.decorators import handle_error, measure_time
from stouputils.parallel import multithreading
from stouputils.print import progress

from ..initialize.source_lore_font import find_pack_png


def get_consistent_timestamp(ctx: Context) -> tuple[int, ...]:
	""" Get a consistent timestamp for archive files based on beet cache .gitignore file modification time. """
	default_time = (2025, 1, 1, 0, 0, 0)  # Default time: 2025-01-01 00:00:00

	try:
		# Use the beet cache .gitignore file modification time for consistent timestamps
		cache_directory = ctx.cache.directory.parent
		default_directory = cache_directory / "default"
		if default_directory.exists():
			time_float = default_directory.stat().st_mtime
			return time.localtime(time_float)[:6]
	except (AttributeError, OSError):
		# Fall back to default time if gitignore file is not available
		pass

	return default_time


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.archive'")
def beet_default(ctx: Context) -> None:
	""" Archive plugin for StewBeet.
	Creates zip archives of the generated data pack and resource pack using pack.dump() to avoid
	interfering with existing pack directories.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	assert ctx.output_directory, "Output directory must be specified in the project configuration."
	assert ctx.packs, "No packs found in the context. Ensure packs are generated before archiving."
	# Ensure output directory exists
	os.makedirs(ctx.output_directory, exist_ok=True)

	consistent_time: tuple[int, ...] = get_consistent_timestamp(ctx)

	# Create archives for each pack
	@handle_error
	def handle_pack(pack: DataPack | ResourcePack) -> None:
		all_items = set(pack.all())
		if not len(all_items) > 0:
			return  # Skip empty packs

		# Get pack name and type
		pack_name: str = ctx.project_name.replace(" ", "") or pack.name or "pack"

		# Determine pack type based on pack attributes
		pack_type: str = "pack"
		if isinstance(pack, DataPack):
			pack_type = "datapack"
		elif isinstance(pack, ResourcePack):
			pack_type = "resource_pack"		# Create archive filename
		archive_path = f"{ctx.output_directory}/{pack_name}_{pack_type}.zip"

		# Create zip archive using pack.dump() to avoid interfering with existing directories
		# This approach writes pack contents directly to a zip file without modifying the original pack structure

		# First pass: Create the zip file normally
		for i in range(10):
			try:
				with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
					pack.dump(zip_file)
				break
			except Exception:
				if i == 9:
					raise
				time.sleep(0.5)

		# Second pass: Read all contents and recreate with consistent timestamps
		# This is necessary because beet's dump() uses origin.open() which bypasses writestr() completely
		temp_contents: dict[str, bytes] = {}
		with zipfile.ZipFile(archive_path, "r") as temp_zip:
			for item in temp_zip.filelist:
				temp_contents[item.filename] = temp_zip.read(item.filename)

		# Check if pack.png exists and prepare it
		pack_png_path = find_pack_png()
		if pack_png_path:
			# Remove pack.png from temp_contents if it exists to avoid duplicates
			temp_contents.pop("pack.png", None)

			# Read pack.png content
			with open(pack_png_path, "rb") as f:
				temp_contents["pack.png"] = f.read()

		# Recreate the zip file with proper timestamps and compression
		with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as final_zip:
			for filename, content in temp_contents.items():
				info = ZipInfo(filename=filename)
				info.date_time = consistent_time
				info.compress_type = zipfile.ZIP_DEFLATED
				final_zip.writestr(info, content)

	# Process each pack in parallel
	multithreading(handle_pack, ctx.packs, max_workers=len(ctx.packs))

