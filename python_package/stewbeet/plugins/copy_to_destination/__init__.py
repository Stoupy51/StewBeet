
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import hashlib
import os
import shutil
import urllib.parse
from dataclasses import dataclass, field

import stouputils as stp
from beet import Context

from ...dependencies.download_manager import get_lib_paths

# Constants
CACHE_NAME: str = "stewbeet_copy_destinations"
""" Beet cache slot holding the sha1 of every file already sent to each remote destination. """
MAX_COPY_WORKERS: int = 8
""" Upper bound on concurrent copies: SFTP puts are latency bound, local copies are disk bound. """


# Classes
@dataclass(frozen=True)
class CopyTask:
	""" A single file to place at a single destination. """
	src: str
	""" Absolute or relative path of the local file to copy. """
	dst: str
	""" Destination, either a local path or an ``sftp://user@host/path`` URL. """
	group: str
	""" Label used to group destinations in the summary log. """

@dataclass
class CopyReport:
	""" Outcome of a batch of copy tasks. """
	copied: set[str] = field(default_factory=set[str])
	""" Groups for which at least one file was actually written. """
	skipped: int = 0
	""" Number of remote files left untouched because they were already up to date. """


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

	# Gather every copy up front so they can all run concurrently
	tasks: list[CopyTask] = []
	if datapack_destinations:
		tasks += _datapack_tasks(output_path, project_name_simple, libs_folder, datapack_destinations)
		tasks += _official_lib_tasks(ctx, datapack_destinations)
	if resource_pack_destinations:
		tasks += _resource_pack_tasks(output_path, project_name_simple, resource_pack_destinations)

	report: CopyReport = _run_copy_tasks(ctx, tasks)

	# Summarize per group, using the destination list the group was built from
	groups: dict[str, list[str]] = {
		"datapacks": datapack_destinations,
		"official libraries": datapack_destinations,
		"resource pack": resource_pack_destinations,
	}
	for group, destinations in groups.items():
		if group in report.copied:
			stp.info(f"Copied {group} to destinations: {', '.join(stp.relative_path(x) for x in destinations)}")
	if report.skipped:
		stp.debug(f"Skipped {report.skipped} remote file(s) already up to date")


def _is_sftp_path(path: str) -> bool:
	return path.startswith("sftp://")


def _datapack_tasks(output_path: str, project_name_simple: str, libs_folder: str, destinations: list[str]) -> list[CopyTask]:
	""" Build the copy tasks for the main datapack and every library datapack.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		libs_folder (str): The folder containing library files.
		destinations (list[str]): List of destination paths for datapacks.
	Returns:
		list[CopyTask]: One task per (file, destination) pair.
	"""
	tasks: list[CopyTask] = []
	main_datapack: str = f"{output_path}/{project_name_simple}_datapack.zip"

	if os.path.exists(main_datapack):
		for dest in destinations:
			tasks.append(CopyTask(main_datapack, f"{dest}/{os.path.basename(main_datapack)}", "datapacks"))

	# Copy all library datapacks
	libs_datapack_path: str = f"{libs_folder}/datapack"
	if libs_folder and os.path.exists(libs_datapack_path):
		for lib_zip in os.listdir(libs_datapack_path):
			if lib_zip.endswith(".zip"):
				for dest in destinations:
					tasks.append(CopyTask(f"{libs_datapack_path}/{lib_zip}", f"{dest}/{lib_zip}", "datapacks"))
	return tasks


def _resource_pack_tasks(output_path: str, project_name_simple: str, destinations: list[str]) -> list[CopyTask]:
	""" Build the copy tasks for the resource pack, preferring the merged one when it exists.

	Args:
		output_path (str): The output directory path.
		project_name_simple (str): The simplified project name.
		destinations (list[str]): List of destination paths for resource packs.
	Returns:
		list[CopyTask]: One task per destination.
	"""
	merged_resource_pack: str = f"{output_path}/{project_name_simple}_resource_pack_with_libs.zip"
	normal_resource_pack: str = f"{output_path}/{project_name_simple}_resource_pack.zip"
	is_merged: bool = os.path.exists(merged_resource_pack)
	resource_pack_to_copy: str = merged_resource_pack if is_merged else normal_resource_pack

	if not os.path.exists(resource_pack_to_copy):
		return []

	# Keep the "_with_libs" suffix in the destination name only when the merged pack is used
	dest_name: str = f"{project_name_simple}_resource_pack{'_with_libs' if is_merged else ''}.zip"
	return [CopyTask(resource_pack_to_copy, f"{dest}/{dest_name}", "resource pack") for dest in destinations]


def _official_lib_tasks(ctx: Context, datapack_destinations: list[str]) -> list[CopyTask]:
	""" Build the copy tasks for every downloaded official library.

	Args:
		ctx (Context): The beet context (used to resolve download paths).
		datapack_destinations (list[str]): List of destination paths for datapacks.
	Returns:
		list[CopyTask]: One task per (library, destination) pair.
	"""
	tasks: list[CopyTask] = []
	for dl in get_lib_paths(ctx):
		if not dl.datapack_path or not os.path.exists(dl.datapack_path):
			continue
		for dest in datapack_destinations:
			tasks.append(CopyTask(dl.datapack_path, f"{dest}/{dl.name}.zip", "official libraries"))
	return tasks


def _file_sha1(path: str) -> str:
	""" Hash a file with sha1, reading it in chunks.

	Args:
		path (str): Path of the file to hash.
	Returns:
		str: Hexadecimal digest.
	"""
	digest = hashlib.sha1()
	with open(path, "rb") as f:
		while chunk := f.read(1 << 20):
			digest.update(chunk)
	return digest.hexdigest()


@stp.simple_cache
def _sftp_password(netloc: str, explicit: str | None) -> str | None:
	""" Resolve the SFTP password from the URL, falling back to the stewbeet credentials file.

	Cached for the whole build: every copy task resolves its destination, and re-parsing the
	credentials file each time costs more than the upload it is preparing.

	Args:
		netloc   (str):        The ``user@host`` part of the destination URL, used as credentials key.
		explicit (str | None): Password embedded in the URL, if any.
	Returns:
		str | None: The password to authenticate with, or None to let paramiko try its keys.
	"""
	if explicit:
		return explicit
	creds_path: str = stp.clean_path("~/stewbeet/credentials.yml")
	if not os.path.exists(creds_path):
		return None
	import yaml
	with open(creds_path) as f:
		creds = yaml.safe_load(f)
	return creds.get("sftp", {}).get(netloc, {}).get("password")


def _sftp_filesystem(dst: str):  # type: ignore[no-untyped-def]
	""" Open (or reuse) the fsspec SFTP filesystem for a destination URL.

	fsspec mixes ``threading.get_ident()`` into its instance cache key, so the connection is shared
	between every destination of the same host within a thread, but each copy worker opens its own.

	Args:
		dst (str): SFTP destination URL (sftp://user[:pass]@host[:port]/path).
	Returns:
		The fsspec SFTP filesystem, and the remote path parsed out of the URL.
	"""
	import fsspec  # type: ignore  # Local import: pulls in paramiko, useless for local-only destinations

	parsed = urllib.parse.urlparse(dst)
	password: str | None = _sftp_password(parsed.netloc, parsed.password)

	# With a password in hand, skip paramiko's key hunt: it decrypts every ~/.ssh key and burns a
	# failed publickey round trip before falling back to the password anyway.
	credentials: dict[str, bool] = {"look_for_keys": False, "allow_agent": False} if password else {}
	fs = fsspec.filesystem(  # type: ignore
		"sftp",
		host=parsed.hostname,
		username=parsed.username,
		password=password,
		port=parsed.port or 22,
		**credentials,
	)
	return fs, parsed.path


def _deduplicate_tasks(tasks: list[CopyTask]) -> list[CopyTask]:
	""" Drop tasks that would write the same file twice.

	Local destinations are compared after resolving symlinks, so two configured folders pointing
	at the same directory (a common Minecraft ``resourcepacks`` setup) are copied to only once,
	instead of racing each other on the same file.

	Args:
		tasks (list[CopyTask]): The tasks to filter.
	Returns:
		list[CopyTask]: The tasks with duplicate destinations removed, order preserved.
	"""
	unique: list[CopyTask] = []
	seen: set[str] = set()
	for task in tasks:
		key: str = task.dst if _is_sftp_path(task.dst) else os.path.normcase(os.path.realpath(task.dst))
		if key not in seen:
			seen.add(key)
			unique.append(task)
	return unique


def _run_copy_tasks(ctx: Context, tasks: list[CopyTask]) -> CopyReport:
	""" Run every copy task, in parallel, skipping remote files that are already up to date.

	Remote destinations are the expensive ones: most of what gets uploaded (music libraries,
	bookshelf modules, ...) is byte-identical from one build to the next. The sha1 of what was
	last sent to each destination is kept in the beet cache and compared against the local file,
	so only genuinely changed files travel over the network.

	Args:
		ctx (Context): The beet context, used for the upload cache.
		tasks (list[CopyTask]): The copy tasks to execute.
	Returns:
		CopyReport: Which groups wrote something, and how many uploads were skipped.
	"""
	# Drop duplicates: two configured destinations can be the same folder through a symlink
	tasks = _deduplicate_tasks(tasks)
	report: CopyReport = CopyReport()
	if not tasks:
		return report

	cache = ctx.cache[CACHE_NAME]
	uploaded: dict[str, str] = cache.json.setdefault("uploaded", {})

	# Hash each distinct source once, only when a remote destination needs it
	remote_tasks: list[CopyTask] = [task for task in tasks if _is_sftp_path(task.dst)]
	hashes: dict[str, str] = {src: _file_sha1(src) for src in {t.src for t in remote_tasks} if os.path.exists(src)}

	# Connect and list the remote directories once, before any thread starts. Listing is a single
	# round trip per directory and keeps the sha1 cache honest: a file deleted or truncated
	# server-side is uploaded again instead of being wrongly considered up to date.
	missing_dirs: set[str] = set()
	listed_dirs: set[str] = set()
	remote_sizes: dict[str, int] = {}
	for dst in {t.dst for t in remote_tasks}:
		fs, remote_path = _sftp_filesystem(dst)
		remote_dir: str = os.path.dirname(remote_path)
		if remote_dir in listed_dirs or remote_dir in missing_dirs:
			continue
		if not fs.exists(remote_dir):
			stp.warning(f"Remote directory '{remote_dir}' does not exist. Cannot copy to '{dst}'.")
			missing_dirs.add(remote_dir)
			continue
		listed_dirs.add(remote_dir)
		remote_sizes.update({str(entry["name"]): int(entry["size"]) for entry in fs.ls(remote_dir, detail=True)})

	def is_up_to_date(task: CopyTask) -> bool:
		""" True when the exact same bytes are already sitting at this destination. """
		_, remote_path = _sftp_filesystem(task.dst)
		return (
			uploaded.get(task.dst) == hashes.get(task.src, "")
			and remote_sizes.get(remote_path) == os.path.getsize(task.src)
		)

	pending_remote: list[CopyTask] = [t for t in remote_tasks if not is_up_to_date(t)]
	report.skipped = len(remote_tasks) - len(pending_remote)

	def run_task(task: CopyTask) -> tuple[str, bool]:
		""" Returns (group, copied). """
		if not _is_sftp_path(task.dst):
			return task.group, _copy_local(task.src, task.dst)

		fs, remote_path = _sftp_filesystem(task.dst)
		if os.path.dirname(remote_path) in missing_dirs:
			return task.group, False

		fs.put(task.src, remote_path)
		if task.src in hashes:
			uploaded[task.dst] = hashes[task.src]
		return task.group, True

	runnable: list[CopyTask] = [t for t in tasks if not _is_sftp_path(t.dst)] + pending_remote
	if not runnable:
		return report

	results: list[tuple[str, bool]] = stp.multithreading(run_task, runnable, max_workers=min(MAX_COPY_WORKERS, len(runnable)))
	report.copied = {group for group, copied in results if copied}

	cache.json["uploaded"] = uploaded
	return report


def _copy_local(src: str, dst: str, max_retries: int = 10, delay: float = 1.0) -> bool:
	""" Copy a file on the local filesystem, retrying through the transient locks Minecraft holds.

	Args:
		src (str): Source file path.
		dst (str): Destination file path.
		max_retries (int): Maximum number of retry attempts.
		delay (float): Delay in seconds between retries.
	Returns:
		bool: True if the file was copied.
	"""
	# Delete the destination file if it exists (optional, best effort)
	try:
		os.remove(dst)
	except OSError:
		pass

	# Ensure the destination directory exists
	dest_dir: str = os.path.dirname(dst)
	if not os.path.exists(dest_dir):
		stp.warning(f"Destination directory '{dest_dir}' does not exist. Cannot copy file '{src}'.")
		return False

	stp.retry(shutil.copy, exceptions=PermissionError, max_attempts=max_retries, delay=delay)(src, dst)
	return True
