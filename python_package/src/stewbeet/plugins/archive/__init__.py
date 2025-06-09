"""
StewBeet Archive Plugin

This plugin replaces the legacy `make_archive.py` system with a beet-compatible implementation.
Instead of using the old `FILES_TO_WRITE` global dictionary approach, this plugin leverages
beet's native Context and pack management system.

Key improvements over the legacy system:
1. Uses beet's Context.packs to access generated data and resource packs
2. Uses pack.dump() to create zip archives without interfering with existing pack directories
3. Integrates with beet's output directory management
4. Provides proper error handling for file operations
5. Uses beet cache .gitignore file modification time for consistent, reproducible timestamps

The plugin automatically:
- Detects all generated packs (data pack and resource pack)
- Creates zip archives with consistent timestamps based on beet cache .gitignore file
- Applies deterministic compression settings for reproducible builds
- Saves archives to the configured output directory
- Preserves existing pack directory structure

Timestamp Strategy:
The plugin uses the modification time of the `.beet_cache/.gitignore` file to ensure
all zip entries have consistent timestamps, making the archives reproducible and
deterministic across builds. This approach is more reliable than searching for
pack.mcmeta files in the output directory.

This replaces the legacy make_archive() function calls and integrates seamlessly
with beet's plugin architecture and build pipeline without deleting the original pack folders.
"""

# Imports
import os
import time
import zipfile
from zipfile import ZipInfo

from beet import Context, DataPack, ResourcePack
from stouputils.decorators import handle_error, measure_time
from stouputils.parallel import multithreading
from stouputils.print import progress


def get_consistent_timestamp(ctx: Context) -> tuple[int, ...]:
	""" Get a consistent timestamp for archive files based on beet cache .gitignore file modification time. """
	default_time = (2025, 1, 1, 0, 0, 0)  # Default time: 2025-01-01 00:00:00

	try:
		# Use the beet cache .gitignore file modification time for consistent timestamps
		cache_directory = ctx.cache.directory.parent
		gitignore_path = cache_directory / ".gitignore"
		if gitignore_path.exists():
			time_float = gitignore_path.stat().st_mtime
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
		with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
			pack.dump(zip_file)

		# Second pass: Read all contents and recreate with consistent timestamps
		# This is necessary because beet's dump() uses origin.open() which bypasses writestr() completely
		temp_contents: dict[str, bytes] = {}
		with zipfile.ZipFile(archive_path, "r") as temp_zip:
			for item in temp_zip.filelist:
				temp_contents[item.filename] = temp_zip.read(item.filename)

		# Recreate the zip file with proper timestamps and compression
		with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as final_zip:
			for filename, content in temp_contents.items():
				info = ZipInfo(filename=filename)
				info.date_time = consistent_time
				info.compress_type = zipfile.ZIP_DEFLATED
				final_zip.writestr(info, content)

	# Process each pack in parallel
	multithreading(handle_pack, ctx.packs, max_workers=len(ctx.packs))

