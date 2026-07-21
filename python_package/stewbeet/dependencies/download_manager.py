""" Dynamic dependency download manager for StewBeet.

Downloads official libraries on first use via beet's content-addressed cache
(``ctx.cache["stewbeet"]``).  Three providers are supported:

1. **Smithed API** — ``bs.*`` and ``smithed.*`` libs
2. **Modrinth API** — ``itemio`` (and future Modrinth libs)
3. **Static URLs** — ``common_signals``, ``furnace_nbt_recipes``, etc.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import stouputils as stp
from beet import Context
from stouputils.typing import JsonDict

from ..core.constants import LATEST_MC_VERSION
from .official_libs import OFFICIAL_LIBS

SMITHED_API_BASE: str = "https://api.smithed.dev/v2/packs"
MODRINTH_API_BASE: str = "https://api.modrinth.com/v2"
HEADERS: dict[str, str] = {"User-Agent": "StewBeet"}
BUILD_CACHE: dict[str, list[DownloadedLib]] = {}  # cache-dir -> results


@dataclass(slots=True)
class DownloadedLib:
	lib_ns: str
	name: str
	version: tuple[int, ...]
	datapack_path: str | None
	resource_pack_path: str | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def mc_tuple(ctx: Context) -> tuple[int, ...]:
	return tuple(int(x) for x in (ctx.minecraft_version or LATEST_MC_VERSION).split(".") if x.isdigit())


def mc_str(ctx: Context) -> str:
	return ctx.minecraft_version or LATEST_MC_VERSION


def lookup_static(lib_data: JsonDict, mc_tup: tuple[int, ...]) -> tuple[tuple[int, ...], str] | None:
	"""Return ``(dep_ver, url)`` for the highest MC key ``<= mc_tup``, or ``None``."""
	best: tuple[tuple[int, ...], tuple[int, ...], str] | None = None
	for (mc_key, dep_ver), url in lib_data.get("static_urls", {}).items():
		if mc_key <= mc_tup and (best is None or mc_key > best[0]):
			best = (mc_key, dep_ver, url)
	return (best[1], best[2]) if best else None


def cached_json(ctx: Context, url: str) -> Any | None:
	try:
		path: Path = ctx.cache["stewbeet"].download(url, headers=HEADERS)
		return json.loads(path.read_text(encoding="utf-8"))
	except Exception as exc:
		stp.warning(f"Failed to fetch '{url}': {exc}")
		return None


def cached_zip(ctx: Context, url: str) -> Path | None:
	"""Download *url* via beet cache, ensuring the file has a ``.zip`` suffix."""
	if not url or url == "can't find":
		return None
	try:
		cache = ctx.cache["stewbeet"]
		path = cache.get_path(url)
		if not path.suffix:
			path = path.with_suffix(".zip")
		return cache.download(url, path, headers=HEADERS)
	except Exception as exc:
		stp.warning(f"Failed to download '{url}': {exc}")
		return None


def version_str(ver: list[int] | tuple[int, ...]) -> str:
	return ".".join(str(x) for x in ver)


def parse_version(s: str) -> tuple[int, ...]:
	return tuple(int(x) for x in s.strip("v").split(".") if x.isdigit())


def mc_compatible(versions: list[JsonDict], mc_tup: tuple[int, ...]) -> list[JsonDict]:
	"""Return versions whose supports list includes mc_tup (exact), falling back to max(supports) <= mc_tup."""
	def sup_tuples(v: JsonDict) -> list[tuple[int, ...]]:
		return [parse_version(s) for s in v.get("supports", [])]
	exact = [v for v in versions if mc_tup in sup_tuples(v)]
	if exact:
		return exact
	return [v for v in versions if sup_tuples(v) and max(sup_tuples(v)) <= mc_tup]


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

def resolve_smithed_lib(ctx: Context, lib_ns: str, lib_data: JsonDict, mc_tup: tuple[int, ...]) -> DownloadedLib | None:
	smithed_id = lib_data.get("smithed_id") or ("bookshelf-" + lib_ns[3:])
	target: str | None = version_str(lib_data["version"]) if "version" in lib_data else None

	data = cached_json(ctx, f"{SMITHED_API_BASE}/{smithed_id}")
	if not data or "versions" not in data:
		stp.warning(f"Smithed API returned no data for '{smithed_id}'. Skipping.")
		return None

	versions: list[JsonDict] = data["versions"]
	if target:
		# Pinned version: find exact match, fall back to latest compatible
		match = next((v for v in versions if v.get("name") == target), None)
		if match is None:
			compat = mc_compatible(versions, mc_tup)
			match = max(compat or versions, key=lambda v: parse_version(v.get("name", "0.0.0")), default=None)
			if match:
				stp.warning(f"Smithed '{smithed_id}' v{target} not found; using v{match['name']} instead.")
	else:
		# No pinned version: pick latest compatible with user's MC
		compat = mc_compatible(versions, mc_tup)
		match = max(compat or versions, key=lambda v: parse_version(v.get("name", "0.0.0")), default=None)

	if match is None:
		stp.warning(f"Smithed '{smithed_id}': no versions available. Skipping.")
		return None

	downloads: JsonDict = match.get("downloads", {})
	dp = cached_zip(ctx, downloads.get("datapack", ""))
	rp = cached_zip(ctx, downloads.get("resourcepack", ""))
	if dp is None:
		stp.warning(f"No datapack download for Smithed '{smithed_id}'. Skipping.")
		return None

	ver = parse_version(match["name"])
	lib_data["version"] = list(ver)
	return DownloadedLib(lib_ns, lib_data["name"], ver, str(dp), str(rp) if rp else None)


def resolve_modrinth_lib(ctx: Context, lib_ns: str, lib_data: JsonDict, mc_ver: str) -> DownloadedLib | None:
	slug = lib_data["modrinth_slug"]
	base = f"{MODRINTH_API_BASE}/project/{slug}/version"

	versions = cached_json(ctx, f"{base}?game_versions=[%22{mc_ver}%22]&loaders=[%22datapack%22]")
	if not versions:
		versions = cached_json(ctx, f"{base}?loaders=[%22datapack%22]")
	if not versions:
		stp.warning(f"No Modrinth release for '{slug}' (MC {mc_ver}). Skipping.")
		return None

	releases = [v for v in versions if v.get("version_type") == "release"]
	vd: JsonDict = (releases or versions)[0]
	ver = parse_version(vd.get("version_number", "0.0.0"))

	files: list[JsonDict] = vd.get("files", [])
	primary = next((f for f in files if f.get("primary")), files[0] if files else None)
	if not primary:
		stp.warning(f"No download file for Modrinth '{slug}'.")
		return None

	lib_data["version"] = list(ver)
	dp = cached_zip(ctx, primary["url"])
	if dp is None:
		return None
	non_primary = [f for f in files if not f.get("primary")]
	rp = cached_zip(ctx, non_primary[0]["url"]) if non_primary else None

	return DownloadedLib(lib_ns, lib_data["name"], ver, str(dp), str(rp) if rp else None)


def resolve_static_lib(ctx: Context, lib_ns: str, lib_data: JsonDict, mc_tup: tuple[int, ...], mc_ver: str) -> DownloadedLib | None:
	entry = lookup_static(lib_data, mc_tup)
	if entry is None:
		stp.warning(f"No static URL for '{lib_ns}' (MC {mc_ver}). Skipping.")
		return None
	dep_ver, url = entry
	if url == "can't find":
		stp.warning(f"Download URL for '{lib_ns}' (MC {mc_ver}) not yet configured. Skipping.")
		return None

	lib_data["version"] = list(dep_ver)
	dp = cached_zip(ctx, url)
	if dp is None:
		return None
	return DownloadedLib(lib_ns, lib_data["name"], dep_ver, str(dp), None)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

@stp.handle_error
def get_lib_paths(ctx: Context) -> list[DownloadedLib]:
	""" Download all ``is_used`` official libs and return their cached paths.

	Results are memoised per build so weld.py and copy_to_destination can
	both call this without redundant work.
	"""
	cache_key = str(ctx.cache["stewbeet"].directory)
	if cache_key in BUILD_CACHE:
		return BUILD_CACHE[cache_key]

	ctx.cache["stewbeet"].timeout(days=30)
	mc_t = mc_tuple(ctx)
	mc_v = mc_str(ctx)

	# Collect every lib to resolve first, then fetch them in parallel (network bound);
	# results keep the input order because weld merges packs in this order.
	tasks: list[tuple[str, JsonDict, str]] = []
	for lib_ns, lib_data in OFFICIAL_LIBS.items():
		if not lib_data.get("is_used", False):
			continue
		source = lib_data.get("source", "")
		if source in ("smithed", "modrinth", "static"):
			tasks.append((lib_ns, lib_data, source))

	# Also process custom load_dependencies entries that specify a source
	load_deps: JsonDict = ctx.meta.get("stewbeet", {}).get("load_dependencies", {})
	for lib_ns, lib_data in load_deps.items():
		source = lib_data.get("source", "")
		if not source:
			continue  # old-format entry with explicit version — nothing to download
		if source in ("smithed", "modrinth", "static"):
			tasks.append((lib_ns, lib_data, source))
		else:
			stp.warning(f"Unknown source '{source}' for load_dependency '{lib_ns}'. Skipping download.")

	def resolve(task: tuple[str, JsonDict, str]) -> DownloadedLib | None:
		lib_ns, lib_data, source = task
		if source == "smithed":
			return resolve_smithed_lib(ctx, lib_ns, lib_data, mc_t)
		if source == "modrinth":
			return resolve_modrinth_lib(ctx, lib_ns, lib_data, mc_v)
		return resolve_static_lib(ctx, lib_ns, lib_data, mc_t, mc_v)

	resolved: list[DownloadedLib | None] = stp.multithreading(resolve, tasks, max_workers=min(8, len(tasks))) if tasks else []
	results: list[DownloadedLib] = [r for r in resolved if r]

	BUILD_CACHE[cache_key] = results
	return results
