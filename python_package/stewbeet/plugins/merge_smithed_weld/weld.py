
# Imports
import logging
import os
import shutil
import sys
import tempfile
import time
from collections.abc import Generator
from glob import glob
from pathlib import Path
from zipfile import ZIP_DEFLATED

import stouputils as stp
from beet import Context, DataPack, ProjectCache, ResourcePack
from stouputils.ctx import Muffle

from ...dependencies.download_manager import get_lib_paths
from ..archive import ConstantTimeZipFile, get_consistent_timestamp
from ..initialize.project_images import find_pack_png

# Constants
ALL_PACK_TYPES: tuple[str, ...] = ("datapack", "resource_pack")
""" Pack types that can be merged with their libraries. """
WELDED_META_KEY: str = "merge_smithed_weld_done"
""" ctx.meta key listing the pack types welded during this build. """
ASKED_PACK_TYPES: str = "merge_smithed_weld_asked"
""" ctx.meta key listing the pack types that were asked to be welded. """


def gather_packs(ctx: Context, pack_type: str) -> list[str]:
	""" Collect the zip paths to merge for the given pack type ("datapack" or "resource_pack").

	Returns absolute paths, main pack last (so it overwrites pack format).
	"""
	stewbeet_config = ctx.meta.get("stewbeet", {})
	libs_folder = stewbeet_config.get("libs_folder", "libs")
	project_name_simple = ctx.project_name.replace(" ", "")

	to_merge: list[str] = [
		str(Path(str(ctx.output_directory)) / f"{project_name_simple}_{pack_type}.zip")
	]
	if libs_folder and os.path.exists(libs_folder):
		to_merge.append(f"{libs_folder}/{pack_type}/*.zip")

	# Add the used official libs (downloaded dynamically)
	for dl in get_lib_paths(ctx):
		lib_path: str | None = dl.datapack_path if pack_type == "datapack" else dl.resource_pack_path
		if lib_path:
			to_merge.append(lib_path)
	expanded: list[str] = [os.path.abspath(x) for pack in to_merge for x in glob(pack)]
	expanded.reverse()	# Reverse so the main pack is last (overwrites pack format)
	return expanded


def weld_to(ctx: Context, sources: list[str], dest_path: str, pack_type: str) -> None:
	""" Weld ``sources`` into ``dest_path`` in a single compression pass.

	Runs the Smithed Weld merge programmatically, then dumps the merged pack straight into
	a :class:`~..archive.ConstantTimeZipFile` (constant timestamps, fixed pack.mcmeta and
	pack.png appended last) instead of letting weld save a temporary zip that would need to
	be fully re-deflated. Also avoids weld's CLI-shared global cache directory, so multiple
	projects can build concurrently.
	"""
	from smithed.weld.toolchain.helpers import run_weld  # pyright: ignore[reportMissingTypeStubs]

	constant_time = get_consistent_timestamp(ctx)

	# Give each weld its own throwaway cache: with `cache=False` beet would build in a temporary
	# directory and os.chdir into it, which is process-global and races when both welds run in
	# parallel (and previously the weld CLI shared one global cache dir across ALL projects,
	# breaking concurrent `stewbeet` runs).
	cache_dir: str = tempfile.mkdtemp(prefix="stewbeet_weld_cache_")
	weld_cache = ProjectCache(directory=Path(cache_dir) / "beet_cache", generated_directory=Path(cache_dir) / "generated")
	try:
		with run_weld(sources, cache=weld_cache) as weld_ctx:
			merged: DataPack | ResourcePack = weld_ctx.data if pack_type == "datapack" else weld_ctx.assets
			local: DataPack | ResourcePack = ctx.data if pack_type == "datapack" else ctx.assets

			with ConstantTimeZipFile(
				dest_path, "w", compression=ZIP_DEFLATED, compresslevel=6,
				date_time=constant_time, skip_names=("pack.mcmeta", "pack.png"),
			) as zip_file:
				merged.dump(zip_file)

				# Add the fixed pack.mcmeta with constant_time
				if hasattr(local, "mcmeta") and local.mcmeta:
					zip_file.force_writestr("pack.mcmeta", local.mcmeta.text.encode("utf-8"))

				# Check if pack.png exists and add it if it does
				pack_png_path = find_pack_png()
				if pack_png_path:
					with open(pack_png_path, "rb") as f:
						zip_file.force_writestr("pack.png", f.read())
	finally:
		shutil.rmtree(cache_dir, ignore_errors=True)


def prepare_weld(ctx: Context, dest_path: str, pack_type: str) -> list[str] | None:
	""" Gather the packs to merge, or return None (with a warning) when welding should be skipped. """
	to_merge: list[str] = gather_packs(ctx, pack_type)

	# Skip welding if there are less than 2 packs to merge
	if len(to_merge) < 2:
		pack_label: str = "datapacks" if pack_type == "datapack" else "resource packs"
		stp.warning(f"No {pack_label} or libs to merge for {dest_path}. Skipping weld.", file=sys.stdout)
		return None

	try:
		import smithed.weld  # noqa: F401  # pyright: ignore[reportMissingTypeStubs, reportUnusedImport]
	except Exception as e:
		stp.error(f"Smithed Weld merging failed: {e}\nThe 'smithed' package is not yet up to date with Python 3.14, consider installing from this fork:\npip install git+https://github.com/Stoupy51/smithed-python.git")
		return None

	return to_merge


def weld_pack(ctx: Context, dest_path: str, pack_type: str) -> float:
	""" Merge a pack and its libs into one file using Weld.

	Args:
		ctx       (Context): The beet context
		dest_path (str):     The path to the destination file
		pack_type (str):     Either "datapack" or "resource_pack"
	Returns:
		float: The time it took to merge the pack and libs
	"""
	start_time: float = time.perf_counter()

	to_merge: list[str] | None = prepare_weld(ctx, dest_path, pack_type)
	if to_merge is not None:
		weld_to(ctx, to_merge, dest_path, pack_type)

	# Return the time it took to merge the pack and libs
	return time.perf_counter() - start_time


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
	return weld_pack(ctx, dest_path, "datapack")


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
	return weld_pack(ctx, dest_path, "resource_pack")


def merged_archive_path(ctx: Context, pack_type: str) -> str:
	""" Path of the ``_with_libs.zip`` produced for a pack type.

	Args:
		ctx       (Context): The beet context.
		pack_type (str):     Either "datapack" or "resource_pack".
	Returns:
		str: The absolute destination path of the merged archive.
	"""
	return str(Path(str(ctx.output_directory)) / f"{ctx.project_name.replace(' ', '')}_{pack_type}_with_libs.zip")


def drop_unwelded_archives(ctx: Context) -> None:
	""" Delete the merged archive of every pack type not welded so far.

	A stale ``_with_libs.zip`` left in the output directory would be picked up by ``compute_sha1``
	and by a release upload, so it has to be gone before the rest of the pipeline looks at the
	output directory. When another entry point welds that pack type later in the pipeline it simply
	writes the archive again, hence the silence here: :func:`report_unwelded_archives` does the
	reporting once the full set of weld entry points is known.

	Args:
		ctx (Context): The beet context.
	"""
	for pack_type in ALL_PACK_TYPES:
		dest: str = merged_archive_path(ctx, pack_type)
		if pack_type not in ctx.meta.get(WELDED_META_KEY, []) and os.path.exists(dest):
			os.remove(dest)


def report_unwelded_archives(ctx: Context) -> Generator[None]:
	""" After the whole pipeline ran, report the pack types no entry point ever welded.

	Registered once by :func:`weld_pack_types` and resumed at the end of the build, so it sees every
	weld entry point that took part regardless of the order they appear in the pipeline.

	Args:
		ctx (Context): The beet context.
	"""
	yield
	for pack_type in ctx.meta.get(ASKED_PACK_TYPES, []):
		if pack_type not in ctx.meta.get(WELDED_META_KEY, []):
			stp.debug(f"No '{os.path.basename(merged_archive_path(ctx, pack_type))}' produced (no pipeline entry welds the {pack_type})")


def weld_pack_types(ctx: Context, pack_types: tuple[str, ...]) -> None:
	""" Merge the given pack types with their libraries.

	Args:
		ctx        (Context):         The beet context.
		pack_types (tuple[str, ...]): The pack types to merge, among :data:`ALL_PACK_TYPES`.
	"""
	# Assertions
	assert ctx.output_directory, "Output directory must be specified in the project configuration."
	assert ctx.project_name, "Project name must be specified in the project configuration."

	# Ensure output directory exists
	os.makedirs(ctx.output_directory, exist_ok=True)

	# Register the pack types that were asked to be welded
	ctx.meta.setdefault(ASKED_PACK_TYPES, []).extend(pack_types)

	# Register the end-of-build report on the first weld entry point of the pipeline
	if WELDED_META_KEY not in ctx.meta:
		ctx.meta[WELDED_META_KEY] = []
		ctx.require(report_unwelded_archives)
	welded: list[str] = ctx.meta[WELDED_META_KEY]

	# Gather sources for each pack that has a base archive (warnings stay visible: this runs unmuffled)
	project_name_simple: str = ctx.project_name.replace(" ", "")
	tasks: list[tuple[list[str], str, str]] = []
	for pack_type in pack_types:
		source: str = str(Path(ctx.output_directory) / f"{project_name_simple}_{pack_type}.zip")
		if os.path.exists(source):
			to_merge: list[str] | None = prepare_weld(ctx, merged_archive_path(ctx, pack_type), pack_type)
			if to_merge is not None:
				tasks.append((to_merge, merged_archive_path(ctx, pack_type), pack_type))
				welded.append(pack_type)
	drop_unwelded_archives(ctx)

	if not tasks:
		return

	# Run the welds in parallel (they are independent and the zlib work releases the GIL).
	# Weld logs failures through the "weld" logger instead of raising, so capture its (noisy)
	# output around the whole parallel section and only replay it when an error actually happens.
	@stp.handle_error
	def run_weld_task(task: tuple[list[str], str, str]) -> None:
		to_merge, dest, pack_type = task
		weld_to(ctx, to_merge, dest, pack_type)

	with Muffle(mute_stderr=True, replay_on_error=True, error_log_level=logging.ERROR, watch_loggers=["weld"]):
		stp.multithreading(run_weld_task, tasks, max_workers=len(tasks))

