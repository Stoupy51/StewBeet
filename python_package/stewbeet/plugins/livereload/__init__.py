
# Imports
import os
import urllib.parse
from pathlib import Path
from typing import Any

import stouputils as stp
from beet import Context

# Name of the helper datapack zip dropped into remote destinations to trigger reloads
LIVERELOAD_ZIP_NAME: str = "livereload.zip"


def get_local_datapack_destinations(ctx: Context) -> list[str]:
	""" Return the resolved local datapack destinations from `meta.stewbeet.build_copy_destinations.datapack`.

	Args:
		ctx (Context): The beet context.
	Returns:
		list[str]: Resolved absolute paths of local datapack destination folders (may be empty).
	"""
	return [dest for dest in _iter_destinations(ctx, "datapack") if not _is_sftp(dest)]


def get_sftp_datapack_destinations(ctx: Context) -> list[str]:
	""" Return the remote `sftp://` datapack destinations from `meta.stewbeet.build_copy_destinations.datapack`.

	Args:
		ctx (Context): The beet context.
	Returns:
		list[str]: `sftp://` datapack destination URLs (may be empty).
	"""
	return [dest for dest in _iter_destinations(ctx, "datapack") if _is_sftp(dest)]


def get_local_resource_pack_destinations(ctx: Context) -> list[str]:
	""" Return the resolved local resource pack destinations from `meta.stewbeet.build_copy_destinations.resource_pack`.

	Args:
		ctx (Context): The beet context.
	Returns:
		list[str]: Resolved absolute paths of local resource pack destination folders (may be empty).
	"""
	return [dest for dest in _iter_destinations(ctx, "resource_pack") if not _is_sftp(dest)]


def _is_sftp(path: str) -> bool:
	""" Return whether the given destination is a remote `sftp://` URL. """
	return str(path).startswith("sftp://")


def _iter_destinations(ctx: Context, key: str) -> list[str]:
	""" Return `build_copy_destinations[key]`, resolving local paths to absolute and leaving `sftp://` URLs as-is. """
	destinations: list[Any] = ctx.meta.get("stewbeet", {}).get("build_copy_destinations", {}).get(key, [])
	return [str(dest) if _is_sftp(dest) else str(Path(dest).resolve()) for dest in destinations]


def _walk_up_for_log(start: Path) -> str | None:
	""" Return the first ancestor of `start` (inclusive) that contains `logs/latest.log`, else None. """
	return next(
		(str(folder) for folder in (start, *start.parents) if (folder / "logs" / "latest.log").is_file()),
		None,
	)


def find_minecraft_dir(ctx: Context, data_pack_dir: Path | None = None, link_minecraft: str | None = None) -> str | None:
	""" Locate the Minecraft directory holding `logs/latest.log`, used to detect reload confirmations.

	The reload cycle relies on tailing that log to remove the polling datapack after each `/reload`,
	so getting this right is what makes live reloading actually work. Live reload watches the *client*
	`[CHAT]` log, so the client `.minecraft` folder is the correct target even when the datapack is
	deployed to a separate (local or remote/`sftp`) server/world tree. The resource pack destination
	usually lives inside that client folder, which makes it the most reliable place to look.

	Resolution order:
		1. Explicit override `meta.stewbeet.livereload.minecraft` (directory containing `logs/`)
		2. The `beet link` Minecraft directory (if the project is also linked)
		3. Walking up from each local resource pack destination (the client `.minecraft`, where `[CHAT]` is logged)
		4. Walking up from the local datapack destination (singleplayer worlds stored under `.minecraft/saves`)

	Args:
		ctx (Context): The beet context.
		data_pack_dir (Path | None): A local datapack destination folder, if any.
		link_minecraft (str | None): The Minecraft directory from `beet link`, if any.
	Returns:
		str | None: Path to the Minecraft directory, or None if it couldn't be determined.
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


def _sftp_filesystem(url: str) -> tuple[Any, urllib.parse.ParseResult]:
	""" Build an fsspec SFTP filesystem for `url`, resolving the password like `copy_to_destination` does.

	The password is taken from the URL if present, otherwise from `~/stewbeet/credentials.yml` under
	`sftp: {"user@host": {password: ...}}`.

	Args:
		url (str): An `sftp://user@host/path` URL.
	Returns:
		tuple[Any, ParseResult]: The fsspec filesystem and the parsed URL.
	"""
	import fsspec  # type: ignore

	parsed = urllib.parse.urlparse(url)
	password: str | None = parsed.password
	if not password:
		creds_path: str = stp.clean_path("~/stewbeet/credentials.yml")
		if os.path.exists(creds_path):
			import yaml
			with open(creds_path) as f:
				creds = yaml.safe_load(f)
			password = creds.get("sftp", {}).get(parsed.netloc, {}).get("password")

	fs = fsspec.filesystem("sftp", host=parsed.hostname, username=parsed.username, password=password, port=parsed.port or 22)  # type: ignore
	return fs, parsed


def _sftp_upload_livereload(local_zip: Path, datapack_url: str) -> str | None:
	""" Upload the helper zip into a remote `sftp://` datapacks folder.

	Args:
		local_zip (Path): Local path to the helper datapack zip.
		datapack_url (str): The remote `sftp://.../datapacks` destination URL.
	Returns:
		str | None: The remote zip URL (for later cleanup), or None if the upload was skipped.
	"""
	zip_url: str = f"{datapack_url.rstrip('/')}/{LIVERELOAD_ZIP_NAME}"
	try:
		fs, parsed = _sftp_filesystem(zip_url)
		remote_dir: str = os.path.dirname(parsed.path)
		if not fs.exists(remote_dir):
			stp.warning(f"Remote datapacks directory '{remote_dir}' does not exist. Live reload skipped for '{datapack_url}'.")
			return None
		fs.put(str(local_zip), parsed.path)
		return zip_url
	except Exception as e:
		stp.warning(f"Live reload SFTP upload failed for '{datapack_url}': {e}")
		return None


def _sftp_remove_livereload(zip_url: str) -> None:
	""" Remove the previously uploaded helper zip from a remote `sftp://` datapacks folder. """
	try:
		fs, parsed = _sftp_filesystem(zip_url)
		if fs.exists(parsed.path):
			fs.rm(parsed.path)
	except Exception:
		pass


def _livereload_cleanup_server(connection: Any) -> None:
	""" Worker tailing the client's `logs/latest.log` and cleaning up every helper pack once a reload is confirmed.

	Messages are `(minecraft_dir, targets)` where `targets` is a tuple of `(kind, ref)` pairs with
	`kind` in `{"local", "sftp"}`. On each confirmed reload, local helper folders are removed from disk
	and remote helper zips are removed over SFTP, so the next build can re-trigger the reload cycle.

	Args:
		connection (Any): The beet worker connection.
	"""
	import logging

	from beet.contrib.livereload import LIVERELOAD_REGEX, LogWatcher
	from beet.core.utils import remove_path

	logger = logging.getLogger("livereload")
	minecraft_dir: str | None = None
	targets: tuple[tuple[str, str], ...] | None = None

	with LogWatcher() as log_watcher:
		for client in connection:
			for message in client:
				if message == (minecraft_dir, targets):
					continue
				minecraft_dir, targets = message

				if not minecraft_dir:
					logger.warning("Couldn't locate the Minecraft client log. Live reload cleanup disabled.")
					continue

				log_file_path = Path(minecraft_dir) / "logs" / "latest.log"
				if not log_file_path.is_file():
					logger.warning("Couldn't find game log. Live reload cleanup disabled.")
					continue

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
	`meta.stewbeet.build_copy_destinations.datapack` (local **and** remote `sftp://`), in addition to
	the usual `beet link` folder.

	This lets users get automatic in-game `/reload` with nothing more than their existing
	`build_copy_destinations` configuration (no `beet link` required). All methods coexist: a linked
	folder, local copy destinations and remote `sftp://` destinations all get reloaded together.

	The patch is idempotent (safe to call several times, e.g. from both `stewbeet.plugins.initialize`
	and `stewbeet.plugins.livereload`) and is a no-op if livereload isn't installed or no datapack
	destination is configured.

	Args:
		ctx (Context): The beet context.
	"""
	# Only patch when the user actually relies on copy destinations (otherwise vanilla livereload is enough)
	if not get_local_datapack_destinations(ctx) and not get_sftp_datapack_destinations(ctx):
		return

	try:
		import beet.contrib.livereload as livereload_module
		from beet import PackOverwrite
		from beet.contrib.autosave import Autosave
		from beet.contrib.link import LinkManager
		from beet.contrib.livereload import create_livereload_data_pack
	except ImportError:
		return

	# Only patch once per process (`stewbeet watch` reuses the interpreter across builds)
	if getattr(livereload_module, "_stewbeet_copy_patch", False):
		return

	def livereload_with_copy_destinations(ctx: Context) -> None:
		""" Replacement for `beet.contrib.livereload.livereload` supporting local and SFTP copy destinations. """
		if not ctx.data:
			return

		link_manager = ctx.inject(LinkManager)
		linked: str | None = str(Path(link_manager.data_pack).resolve()) if link_manager.data_pack else None

		# Union of the linked folder and all local copy destinations, plus the remote sftp destinations
		local_dirs: list[str] = list(dict.fromkeys(([linked] if linked else []) + get_local_datapack_destinations(ctx)))
		sftp_urls: list[str] = get_sftp_datapack_destinations(ctx)

		cleanup_targets: list[tuple[str, str]] = []
		first_local_dir: Path | None = None

		# Local: drop the tiny polling datapack folder into each destination
		for dir_str in local_dirs:
			data = create_livereload_data_pack()
			try:
				livereload_path: Path = Path(str(data.save(dir_str)))
			except PackOverwrite as exc:
				livereload_path = Path(exc.path)
			cleanup_targets.append(("local", str(livereload_path)))
			if first_local_dir is None:
				first_local_dir = Path(dir_str)

		# SFTP: upload the polling datapack as a zip into each remote datapacks folder
		if sftp_urls:
			import tempfile
			with tempfile.TemporaryDirectory() as tmp:
				local_zip: Path = Path(tmp) / LIVERELOAD_ZIP_NAME
				create_livereload_data_pack().save(path=local_zip, zipped=True)
				for url in sftp_urls:
					if zip_url := _sftp_upload_livereload(local_zip, url):
						cleanup_targets.append(("sftp", zip_url))

		if not cleanup_targets:
			return

		# The reload confirmation is always logged by the *local* client (`[CHAT]`), even for remote servers
		minecraft: str | None = find_minecraft_dir(ctx, first_local_dir, link_manager.minecraft)

		# A single worker tails the client log and cleans up every helper pack (local + remote) on reload
		with ctx.worker(_livereload_cleanup_server) as channel: # type: ignore
			channel.send((minecraft, tuple(cleanup_targets))) # type: ignore

	# Swap the module-level function so livereload.beet_default registers our version with Autosave.
	# Also replace it in any already-registered Autosave handlers (covers the `require` ordering where
	# beet.contrib.livereload was required before StewBeet had a chance to patch it).
	original_livereload = livereload_module.livereload
	livereload_module.livereload = livereload_with_copy_destinations
	livereload_module._stewbeet_copy_patch = True  # type: ignore
	try:
		autosave = ctx.inject(Autosave)
		autosave.link_handlers = [livereload_with_copy_destinations if handler is original_livereload else handler for handler in autosave.link_handlers]
	except Exception:
		pass


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.livereload'")
def beet_default(ctx: Context) -> None:
	""" Live reload wrapper plugin for StewBeet.

	Enables in-game `/reload` on each build through `beet link` and/or the StewBeet
	`build_copy_destinations.datapack` folders (local and remote `sftp://`), then delegates to the
	underlying `beet.contrib.livereload` plugin. Simply require this plugin (or add it to the pipeline)
	instead of wiring up `beet.contrib.livereload` and `beet link` manually.

	Args:
		ctx (Context): The beet context.
	"""
	patch_livereload_for_copy_destinations(ctx)
	ctx.require("beet.contrib.livereload")

