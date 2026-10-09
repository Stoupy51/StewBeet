""" 🗜️ Zips the generated datapack and resource pack. """
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import io
import os
import re
import subprocess
import time
import zipfile
import zlib
from typing import IO, Any, Literal
from zipfile import ZipInfo

import stouputils as stp
from beet import Context, DataPack, ResourcePack
from beet.toolchain.config import locate_config

from ...core.__memory__ import Mem
from ..initialize.beet_patches import reuse_unchanged_png_bytes
from ..initialize.project_images import find_pack_png

# Constants
TEXT_EXTENSIONS: frozenset[str] = frozenset({
	".fsh", ".glsl", ".json", ".lang", ".map", ".mcfunction", ".mcmeta", ".md",
	".properties", ".snbt", ".txt", ".vsh", ".yaml", ".yml",
})
""" Extensions whose entries hold text, so their line endings are normalized on the way into the archive.
Everything else is archived byte for byte, since a CRLF inside a .png or an .ogg is data rather than a line ending. """

BEFORE_NEWLINE: re.Pattern[bytes] = re.compile(rb"\r+\n")
""" Carriage returns opening a line ending, however many of them there are.
A file welded out of a library archive already holding CRLF reaches this as CRCRLF.
TextIOWrapper translates the newline it finds behind the carriage return that was already there.
"""


def get_consistent_timestamp(ctx: Context) -> tuple[int, int, int, int, int, int]:
	""" Date written on every archive entry: the last commit of the beet config, in UTC, identical in every clone.

	A file modification time is not kept by git, so it is only the fallback: the beet cache one, then 2025-01-01.
	"""
	default_time = (2025, 1, 1, 0, 0, 0)  # Default time: 2025-01-01 00:00:00

	config_path = locate_config(ctx.directory)
	if config_path:
		try:
			committed: str = subprocess.run(
				["git", "log", "-1", "--format=%ct", "--", config_path.name],
				cwd=config_path.parent, capture_output=True, text=True, check=False,
			).stdout.strip()
			if committed:
				return time.gmtime(int(committed))[:6]
		except OSError:
			pass  # git is not installed

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

	A text entry is written with Unix line endings whatever the host would have used, see :func:`unix_newlines`.

	When the archive replaces one written before, an entry holding the same bytes as there is copied
	still compressed instead of being deflated again, see :meth:`store`.
	"""

	def __init__(
		self, file: Any, mode: Literal["r", "w", "x", "a"] = "r", *args: Any,
		date_time: tuple[int, int, int, int, int, int], skip_names: tuple[str, ...] = (), **kwargs: Any
	) -> None:
		previous: bytes = b""
		if mode == "w" and isinstance(file, str) and os.path.isfile(file):
			with open(file, "rb") as previous_file:
				previous = previous_file.read()
		super().__init__(file, mode, *args, **kwargs)
		self.date_time: tuple[int, int, int, int, int, int] = date_time
		self.skip_names: set[str] = set(skip_names)
		self.previous: zipfile.ZipFile | None = None
		""" The archive this one replaces, read before it was truncated, to reuse its unchanged entries. """
		self.previous_bytes: bytes = previous
		if previous:
			try:
				self.previous = zipfile.ZipFile(io.BytesIO(previous))
			except zipfile.BadZipFile:
				self.previous = None

	def _forced_info(self, name: str) -> ZipInfo:
		info = ZipInfo(filename=name)
		info.date_time = self.date_time
		info.compress_type = zipfile.ZIP_DEFLATED
		return info

	def open(
		self, name: str | ZipInfo, mode: Literal["r", "w"] = "r", pwd: bytes | None = None, *, force_zip64: bool = False
	) -> IO[bytes]:
		if mode != "w":
			return super().open(name, mode, pwd, force_zip64=force_zip64)
		filename: str = name.filename if isinstance(name, ZipInfo) else name
		if filename in self.skip_names:
			return io.BytesIO()  # Discard the content, the caller will write a fixed version
		return EntryWriter(self, filename)

	def writestr(
		self, zinfo_or_arcname: str | ZipInfo, data: Any, compress_type: int | None = None, compresslevel: int | None = None
	) -> None:
		filename: str = zinfo_or_arcname.filename if isinstance(zinfo_or_arcname, ZipInfo) else zinfo_or_arcname
		if filename in self.skip_names:
			return
		self.store(filename, data.encode("utf-8") if isinstance(data, str) else bytes(data))

	def write(self, filename: Any, arcname: Any = None, compress_type: int | None = None, compresslevel: int | None = None) -> None:
		name: str = str(arcname if arcname is not None else filename)
		if name in self.skip_names:
			return
		with open(filename, "rb") as f:
			self.store(name, f.read())

	def force_writestr(self, name: str, data: bytes) -> None:
		""" Write an entry with the constant timestamp, bypassing ``skip_names``.

		Drops ``name`` from ``skip_names`` first: ``ZipFile.writestr`` internally goes through
		``self.open`` which would otherwise discard the entry again.
		"""
		self.skip_names.discard(name)
		self.writestr(name, data)

	def store(self, name: str, data: bytes) -> None:
		""" Write one entry, with Unix line endings for text, reusing its compressed bytes from the previous archive when unchanged.

		Deflate gives the same bytes for the same input, so the copy is what compressing again would have written.
		The previous entry is decompressed and compared whole: a matching checksum alone is not trusted.
		"""
		normalized: str | bytes = unix_newlines(name, data)
		data = normalized.encode("utf-8") if isinstance(normalized, str) else normalized
		info: ZipInfo = self._forced_info(name)
		info.file_size = len(data)
		internals: Any = self  # ZipFile keeps its writing state in private attributes
		raw: bytes | None = self.previous_raw(name, data)
		fp: IO[bytes] | None = self.fp
		if raw is None or fp is None or not internals._seekable:
			# What ZipFile.writestr does, minus going back through the overridden `open`
			with internals._lock, super().open(info, mode="w") as entry:
				entry.write(data)
			return

		# What ZipFile writes for a new entry, with the compressed bytes taken as they are
		info.flag_bits = 1 << 11  # UTF-8 file name, as ZipFile flags every entry it writes
		info.external_attr = 0o600 << 16
		info.compress_size = len(raw)
		info.CRC = zlib.crc32(data)
		with internals._lock:
			fp.seek(self.start_dir)
			info.header_offset = fp.tell()
			internals._writecheck(info)
			internals._didModify = True
			fp.write(info.FileHeader(zip64=False))
			fp.write(raw)
			self.start_dir = fp.tell()
			self.filelist.append(info)
			self.NameToInfo[name] = info

	def previous_entry(self, name: str) -> bytes | None:
		""" The content of an entry of the archive this one replaces, None when there is no such entry. """
		if self.previous is None:
			return None
		try:
			return self.previous.read(name)
		except KeyError:
			return None

	def previous_raw(self, name: str, data: bytes) -> bytes | None:
		""" The still compressed bytes of the previous archive's entry when it holds exactly data, else None. """
		if self.previous is None:
			return None
		try:
			old: ZipInfo = self.previous.getinfo(name)
		except KeyError:
			return None
		if (
			old.compress_type != zipfile.ZIP_DEFLATED or old.file_size != len(data) or zlib.crc32(data) != old.CRC
			or old.flag_bits & 0x8 or self.previous.read(old) != data
		):
			return None

		# The local header has its own name and extra field lengths, the data follows them
		header: bytes = self.previous_bytes[old.header_offset:old.header_offset + 30]
		data_start: int = old.header_offset + 30 + int.from_bytes(header[26:28], "little") + int.from_bytes(header[28:30], "little")
		return self.previous_bytes[data_start:data_start + old.compress_size]

	def close(self) -> None:
		if self.previous is not None:
			self.previous.close()
			self.previous = None
		self.previous_bytes = b""
		super().close()


class EntryWriter(io.BytesIO):
	""" Collects what is written to one entry, and stores it in the archive once closed.

	>>> archive = ConstantTimeZipFile(io.BytesIO(), "w", date_time=(2025, 1, 1, 0, 0, 0))
	>>> with archive.open("say.mcfunction", "w") as entry:
	...     _ = entry.write(b"say a\\r\\nsay b\\r\\r\\n")
	>>> archive.read("say.mcfunction")
	b'say a\\nsay b\\n'
	"""

	def __init__(self, archive: ConstantTimeZipFile, name: str) -> None:
		super().__init__()
		self.archive: ConstantTimeZipFile = archive
		self.name: str = name

	def close(self) -> None:
		if not self.closed:
			self.archive.store(self.name, self.getvalue())
		super().close()


def is_text_entry(name: str) -> bool:
	""" Whether an archive entry holds text, so its line endings are ours to normalize.

	>>> is_text_entry("data/ns/function/tick.mcfunction"), is_text_entry("pack.png")
	(True, False)
	"""
	return os.path.splitext(name)[1].lower() in TEXT_EXTENSIONS


def unix_lines(data: bytes) -> bytes:
	""" The same bytes with every line ending turned into a LF.

	`bytes.replace` runs eleven times faster than the pattern.
	It covers the CRLF a Windows `TextIOWrapper` writes, which is all but every entry of an archive built here.
	The pattern is only there for a run of carriage returns, which nothing but a welded library archive produces.

	>>> unix_lines(b"say a\\r\\nsay b\\r\\r\\n")
	b'say a\\nsay b\\n'
	"""
	if b"\r\r" in data:
		return BEFORE_NEWLINE.sub(b"\n", data)
	return data.replace(b"\r\n", b"\n")


def unix_newlines(name: str, data: str | bytes) -> str | bytes:
	""" The same data with every line ending turned into a LF, for a text entry only.

	>>> unix_newlines("tick.mcfunction", b"say a\\r\\nsay b\\r\\r\\n"), unix_newlines("icon.png", b"\\r\\n")
	(b'say a\\nsay b\\n', b'\\r\\n')
	"""
	if not is_text_entry(name):
		return data
	if isinstance(data, str):
		return re.sub(BEFORE_NEWLINE.pattern.decode(), "\n", data)
	return unix_lines(data)


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.archive'")
def beet_default(ctx: Context) -> None:
	""" Archive plugin for StewBeet.
	Creates zip archives of the generated datapack and resource pack using pack.dump() to avoid
	interfering with existing pack directories.

	Args:
		ctx: The beet context.
	"""
	# Assertions
	Mem.ctx = ctx
	assert Mem.ctx.output_directory, "Output directory must be specified in the project configuration."

	# Source maps have to be in the pack before it is zipped, and this is the last moment they can be.
	# Flushing here spares projects from placing `stewbeet.plugins.sniffer.emit` by hand, and costs nothing when capture is off.
	if Mem.sniffer_enabled:
		from ..sniffer.emit import write_maps
		write_maps(ctx)

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
		if not pack:
			return  # Skip empty packs

		# Get pack name and type
		pack_name: str = Mem.ctx.project_name.replace(" ", "") or pack.name or "pack"

		# Determine pack type based on pack attributes
		pack_type: str = "datapack" if isinstance(pack, DataPack) else "resource_pack"

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
				# Archive generated images with the bytes the previous archive holds for the same pixels (see reuse_unchanged_pngs)
				reuse_unchanged_png_bytes(pack, zip_file.previous_entry)
				pack.dump(zip_file)
				if pack_png_path:
					zip_file.force_writestr("pack.png", pack_png_content)
		dump_with_retry()

	# Process each pack in parallel (zlib compression releases the GIL)
	packs = list(Mem.ctx.packs)
	stp.multithreading(handle_pack, packs, max_workers=max(1, len(packs)))

