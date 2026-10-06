
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import contextlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import stouputils as stp
from beet import Context

from ..copy_to_destination.sftp import SftpPool, is_sftp_path

if TYPE_CHECKING:
	from beet.contrib.livereload import LogWatcher

# Name of the helper datapack zip dropped into remote destinations to trigger reloads
LIVERELOAD_ZIP_NAME: str = "livereload.zip"


def get_local_datapack_destinations(ctx: Context) -> list[str]:
	""" Return the resolved local datapack destinations from `meta.stewbeet.build_copy_destinations.datapack`.

	Args:
		ctx: The beet context.
	Returns:
		list[str]: Resolved absolute paths of local datapack destination folders (may be empty).
	"""
	return [dest for dest in _iter_destinations(ctx, "datapack") if not is_sftp_path(dest)]


def get_sftp_datapack_destinations(ctx: Context) -> list[str]:
	""" Return the remote `sftp://` datapack destinations from `meta.stewbeet.build_copy_destinations.datapack`.

	Args:
		ctx: The beet context.
	Returns:
		list[str]: `sftp://` datapack destination URLs (may be empty).
	"""
	return [dest for dest in _iter_destinations(ctx, "datapack") if is_sftp_path(dest)]


def get_local_resource_pack_destinations(ctx: Context) -> list[str]:
	""" Return the resolved local resource pack destinations from `meta.stewbeet.build_copy_destinations.resource_pack`.

	Args:
		ctx: The beet context.
	Returns:
		list[str]: Resolved absolute paths of local resource pack destination folders (may be empty).
	"""
	return [dest for dest in _iter_destinations(ctx, "resource_pack") if not is_sftp_path(dest)]


def _iter_destinations(ctx: Context, key: str) -> list[str]:
	""" Return `build_copy_destinations[key]`, resolving local paths to absolute and leaving `sftp://` URLs as-is. """
	destinations: list[Any] = ctx.meta.get("stewbeet", {}).get("build_copy_destinations", {}).get(key, [])
	return [str(dest) if is_sftp_path(dest) else str(Path(dest).resolve()) for dest in destinations]


def _walk_up_for_log(start: Path) -> str | None:
	""" Return the first ancestor of `start` (inclusive) that contains `logs/latest.log`, else None. """
	return next(
		(str(folder) for folder in (start, *start.parents) if (folder / "logs" / "latest.log").is_file()),
		None,
	)


def find_minecraft_dir(ctx: Context, data_pack_dir: Path | None = None, link_minecraft: str | None = None) -> str | None:
	""" Locate the client Minecraft directory holding `logs/latest.log`, None if it cannot be determined.

	Live reload tails that log's `[CHAT]` lines to remove the polling datapack after each `/reload`,
	so it is the client `.minecraft` even when the datapack is deployed to a separate local or `sftp` server.

	Resolution order:
		1. Explicit override `meta.stewbeet.livereload.minecraft` (directory containing `logs/`)
		2. The `beet link` Minecraft directory (if the project is also linked)
		3. Walking up from each local resource pack destination (the client `.minecraft`, where `[CHAT]` is logged)
		4. Walking up from the local datapack destination (singleplayer worlds stored under `.minecraft/saves`)

	Args:
		data_pack_dir:  A local datapack destination folder, if any.
		link_minecraft: The Minecraft directory from `beet link`, if any.
	"""
	# 1. Explicit override (accepted as long as the directory exists, so a not-yet-started game still works)
	override: str = ctx.meta.get("stewbeet", {}).get("livereload", {}).get("minecraft", "")
	if override and Path(override).is_dir():
		return str(Path(override).resolve())

	# 2. The linked Minecraft directory
	if link_minecraft and (Path(link_minecraft) / "logs" / "latest.log").is_file():
		return link_minecraft

	# 3. Resource pack destinations first (client .minecraft), then 4. the datapack destination
	candidates: list[Path] = [Path(p) for p in get_local_resource_pack_destinations(ctx)]
	if data_pack_dir is not None:
		candidates.append(data_pack_dir)
	for start in candidates:
		if found := _walk_up_for_log(start):
			return found
	return None


def _sftp_upload_livereload(local_zip: Path, datapack_url: str) -> str | None:
	""" Upload the helper zip into a remote `sftp://` datapacks folder.

	Args:
		local_zip:    Local path to the helper datapack zip.
		datapack_url: The remote `sftp://.../datapacks` destination URL.
	Returns:
		str | None: The remote zip URL (for later cleanup), or None if the upload was skipped.
	"""
	zip_url: str = f"{datapack_url.rstrip('/')}/{LIVERELOAD_ZIP_NAME}"
	try:
		if SftpPool.list_sizes(zip_url) is None:
			stp.warning(f"Remote datapacks directory does not exist. Live reload skipped for '{datapack_url}'.")
			return None
		SftpPool.put(zip_url, str(local_zip))
		return zip_url
	except Exception as e:
		stp.warning(f"Live reload SFTP upload failed for '{datapack_url}': {e}")
		return None


def _sftp_remove_livereload(zip_url: str) -> None:
	""" Remove the previously uploaded helper zip from a remote `sftp://` datapacks folder. """
	with contextlib.suppress(Exception):
		SftpPool.remove(zip_url)


def _livereload_cleanup_server(connection: Any) -> None:
	""" Worker tailing the client's `logs/latest.log` and cleaning up every helper pack once a reload is confirmed.

	Messages are `(minecraft_dir, targets)` where `targets` is a tuple of `(kind, ref)` pairs with
	`kind` in `{"local", "sftp"}`. On each confirmed reload, local helper folders are removed from disk
	and remote helper zips are removed over SFTP, so the next build can re-trigger the reload cycle.

	Args:
		connection: The beet worker connection.
	"""
	from beet.contrib.livereload import LogWatcher

	logger = logging.getLogger("livereload")
	last: tuple[str | None, tuple[tuple[str, str], ...] | None] = (None, None)
	with LogWatcher() as log_watcher:
		for client in connection:
			for message in client:
				if message != last:
					last = message
					_tail_for_cleanup(log_watcher, message[0], message[1], logger)


def _tail_for_cleanup(
	log_watcher: LogWatcher, minecraft_dir: str | None, targets: tuple[tuple[str, str], ...] | None, logger: logging.Logger
) -> None:
	""" Tail the client log, removing every target once it logs a reload. """
	from beet.contrib.livereload import LIVERELOAD_REGEX
	from beet.core.utils import remove_path

	if not minecraft_dir:
		logger.warning("Couldn't locate the Minecraft client log. Live reload cleanup disabled.")
		return
	log_file_path = Path(minecraft_dir) / "logs" / "latest.log"
	if not log_file_path.is_file():
		logger.warning("Couldn't find game log. Live reload cleanup disabled.")
		return

	active_targets: tuple[tuple[str, str], ...] = targets or ()

	@log_watcher.tail(log_file_path)
	def _(args: dict[str, Any], active_targets: tuple[tuple[str, str], ...] = active_targets):
		if LIVERELOAD_REGEX.search(args["message"]):
			for kind, ref in active_targets:
				if kind == "sftp":
					_sftp_remove_livereload(ref)
				else:
					remove_path(ref)


def patch_livereload_for_copy_destinations(ctx: Context) -> None:
	""" Monkey-patch `beet.contrib.livereload` so live reloading also targets the folders listed in
	`meta.stewbeet.build_copy_destinations.datapack` (local **and** remote `sftp://`), in addition to the usual `beet link` folder.

	This lets users get automatic in-game `/reload` with nothing more than their existing `build_copy_destinations` configuration
	(no `beet link` required). All methods coexist: a linked folder,
	local copy destinations and remote `sftp://` destinations all get reloaded together.

	The patch is idempotent (safe to call several times, e.g.
	from both `stewbeet.plugins.initialize` and `stewbeet.plugins.livereload`) and is a no-op if livereload isn't installed or no
	datapack destination is configured.

	Args:
		ctx: The beet context.
	"""
	# Only patch when the user actually relies on copy destinations (otherwise vanilla livereload is enough)
	if not get_local_datapack_destinations(ctx) and not get_sftp_datapack_destinations(ctx):
		return

	try:
		import beet.contrib.livereload as livereload_module
		from beet.contrib.autosave import Autosave
	except ImportError:
		return

	# Only patch once per process (`stewbeet watch` reuses the interpreter across builds)
	if getattr(livereload_module, "_stewbeet_copy_patch", False):
		return

	# Swap the module-level function so livereload.beet_default registers our version with Autosave,
	# and in the handlers Autosave already holds when beet.contrib.livereload was required before this patch.
	original_livereload = livereload_module.livereload
	livereload_module.livereload = livereload_with_copy_destinations
	livereload_module._stewbeet_copy_patch = True  # pyright: ignore[reportAttributeAccessIssue]
	with contextlib.suppress(Exception):
		autosave = ctx.inject(Autosave)
		autosave.link_handlers = [
			livereload_with_copy_destinations if handler is original_livereload else handler
			for handler in autosave.link_handlers
		]


def livereload_with_copy_destinations(ctx: Context) -> None:
	""" Replacement for `beet.contrib.livereload.livereload` supporting local and SFTP copy destinations. """
	from beet.contrib.link import LinkManager

	if not ctx.data:
		return
	link_manager = ctx.inject(LinkManager)
	linked: str | None = str(Path(link_manager.data_pack).resolve()) if link_manager.data_pack else None

	# Union of the linked folder and all local copy destinations, plus the remote sftp destinations
	local_dirs: list[str] = list(dict.fromkeys(([linked] if linked else []) + get_local_datapack_destinations(ctx)))
	cleanup_targets: list[tuple[str, str]] = _drop_local_packs(local_dirs) + _upload_sftp_packs(get_sftp_datapack_destinations(ctx))
	if not cleanup_targets:
		return

	# The reload confirmation is always logged by the *local* client (`[CHAT]`), even for remote servers
	first_local_dir: Path | None = Path(local_dirs[0]) if local_dirs else None
	minecraft: str | None = find_minecraft_dir(ctx, first_local_dir, link_manager.minecraft)

	# A single worker tails the client log and cleans up every helper pack (local + remote) on reload
	with ctx.worker(_livereload_cleanup_server) as channel:  # pyright: ignore[reportUnknownVariableType]
		channel.send((minecraft, tuple(cleanup_targets)))  # pyright: ignore[reportUnknownMemberType]


def _drop_local_packs(local_dirs: list[str]) -> list[tuple[str, str]]:
	""" Drop the tiny polling datapack folder into each local destination, and return the cleanup target of each. """
	from beet import PackOverwrite
	from beet.contrib.livereload import create_livereload_data_pack

	targets: list[tuple[str, str]] = []
	for dir_str in local_dirs:
		try:
			livereload_path: Path = Path(str(create_livereload_data_pack().save(dir_str)))
		except PackOverwrite as exc:
			livereload_path = Path(exc.path)
		targets.append(("local", str(livereload_path)))
	return targets


def _upload_sftp_packs(sftp_urls: list[str]) -> list[tuple[str, str]]:
	""" Upload the polling datapack as a zip into each remote datapacks folder, and return the cleanup target of each upload. """
	from beet.contrib.livereload import create_livereload_data_pack

	if not sftp_urls:
		return []
	import tempfile
	with tempfile.TemporaryDirectory() as tmp:
		local_zip: Path = Path(tmp) / LIVERELOAD_ZIP_NAME
		create_livereload_data_pack().save(path=local_zip, zipped=True)
		uploaded: list[str | None] = [_sftp_upload_livereload(local_zip, url) for url in sftp_urls]
	return [("sftp", zip_url) for zip_url in uploaded if zip_url]


# Main entry point
def beet_default(ctx: Context) -> None:
	""" Live reload wrapper plugin for StewBeet.

	Enables in-game `/reload` on each build through `beet link` and/or the StewBeet `build_copy_destinations.datapack` folders
	(local and remote `sftp://`), then delegates to the underlying `beet.contrib.livereload` plugin.
	Simply require this plugin (or add it to the pipeline) instead of wiring up `beet.contrib.livereload` and `beet link` manually.

	Args:
		ctx: The beet context.
	"""
	patch_livereload_for_copy_destinations(ctx)
	ctx.require("beet.contrib.livereload")

