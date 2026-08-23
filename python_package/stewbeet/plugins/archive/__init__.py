
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import io
import os
import time
import zipfile
from typing import IO, Any, Literal
from zipfile import ZipInfo

import stouputils as stp
from beet import Context, DataPack, ResourcePack

from ...core.__memory__ import Mem
from ..initialize.project_images import find_pack_png


def get_consistent_timestamp(ctx: Context) -> tuple[int, int, int, int, int, int]:
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


class ConstantTimeZipFile(zipfile.ZipFile):
	""" ZipFile that forces a constant timestamp and normalized metadata on every entry.

	Replaces the old two-pass approach (dump to zip, read everything back, re-deflate with
	fixed timestamps): every write path used by ``pack.dump()`` (``open(mode="w")``,
	``writestr`` and ``write``) goes through a fresh :class:`ZipInfo` carrying the constant
	``date_time``, so a single compression pass produces the exact same bytes.

	Entries whose name is in ``skip_names`` are silently dropped (used to replace
	``pack.mcmeta``/``pack.png`` with fixed content afterwards via :meth:`force_writestr`).
	"""

	def __init__(self, *args: Any, date_time: tuple[int, int, int, int, int, int], skip_names: tuple[str, ...] = (), **kwargs: Any) -> None:
		super().__init__(*args, **kwargs)
		self.date_time: tuple[int, int, int, int, int, int] = date_time
		self.skip_names: set[str] = set(skip_names)

	def _forced_info(self, name: str) -> ZipInfo:
		info = ZipInfo(filename=name)
		info.date_time = self.date_time
		info.compress_type = zipfile.ZIP_DEFLATED
		return info

	def open(self, name: str | ZipInfo, mode: Literal["r", "w"] = "r", pwd: bytes | None = None, *, force_zip64: bool = False) -> IO[bytes]:
		if mode != "w":
			return super().open(name, mode, pwd, force_zip64=force_zip64)
		filename: str = name.filename if isinstance(name, ZipInfo) else name
		if filename in self.skip_names:
			return io.BytesIO()  # Discard the content, the caller will write a fixed version
		return super().open(self._forced_info(filename), mode, pwd, force_zip64=force_zip64)

	def writestr(self, zinfo_or_arcname: str | ZipInfo, data: Any, compress_type: int | None = None, compresslevel: int | None = None) -> None:
		filename: str = zinfo_or_arcname.filename if isinstance(zinfo_or_arcname, ZipInfo) else zinfo_or_arcname
		if filename in self.skip_names:
			return
		super().writestr(self._forced_info(filename), data, compress_type, compresslevel)

	def write(self, filename: Any, arcname: Any = None, compress_type: int | None = None, compresslevel: int | None = None) -> None:
		name: str = str(arcname if arcname is not None else filename)
		if name in self.skip_names:
			return
		with open(filename, "rb") as f:
			super().writestr(self._forced_info(name), f.read(), compress_type, compresslevel)

	def force_writestr(self, name: str, data: bytes) -> None:
		""" Write an entry with the constant timestamp, bypassing ``skip_names``.

		Drops ``name`` from ``skip_names`` first: ``ZipFile.writestr`` internally goes through
		``self.open`` which would otherwise discard the entry again.
		"""
		self.skip_names.discard(name)
		self.writestr(name, data)


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.archive'")
def beet_default(ctx: Context) -> None:
	""" Archive plugin for StewBeet.
	Creates zip archives of the generated datapack and resource pack using pack.dump() to avoid
	interfering with existing pack directories.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	Mem.ctx = ctx
	assert Mem.ctx.output_directory, "Output directory must be specified in the project configuration."

	# Ensure output directory exists
	os.makedirs(Mem.ctx.output_directory, exist_ok=True)

	consistent_time: tuple[int, int, int, int, int, int] = get_consistent_timestamp(Mem.ctx)
	pack_png_path: str = find_pack_png() or ""
	pack_png_content: bytes = b""
	if pack_png_path:
		with open(pack_png_path, "rb") as f:
			pack_png_content = f.read()

	# Create archives for each pack
	@stp.handle_error
	def handle_pack(pack: DataPack | ResourcePack) -> None:
		all_items = set(pack.all())
		if not len(all_items) > 0:
			return  # Skip empty packs

		# Get pack name and type
		pack_name: str = Mem.ctx.project_name.replace(" ", "") or pack.name or "pack"

		# Determine pack type based on pack attributes
		pack_type: str = "pack"
		if isinstance(pack, DataPack):
			pack_type = "datapack"
		else:
			pack_type = "resource_pack"

		# Create archive filename
		archive_path = f"{Mem.ctx.output_directory}/{pack_name}_{pack_type}.zip"

		# Single pass: dump the pack through a ZipFile that forces consistent timestamps,
		# replacing pack.png with the project's icon (appended last, like the old two-pass code).
		@stp.retry(exceptions=Exception, max_attempts=10, delay=0.5)
		def dump_with_retry():
			skip_names: tuple[str, ...] = ("pack.png",) if pack_png_path else ()
			with ConstantTimeZipFile(
				archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6,
				date_time=consistent_time, skip_names=skip_names,
			) as zip_file:
				pack.dump(zip_file)
				if pack_png_path:
					zip_file.force_writestr("pack.png", pack_png_content)
		dump_with_retry()

	# Process each pack in parallel (zlib compression releases the GIL)
	packs = list(Mem.ctx.packs)
	stp.multithreading(handle_pack, packs, max_workers=max(1, len(packs)))

