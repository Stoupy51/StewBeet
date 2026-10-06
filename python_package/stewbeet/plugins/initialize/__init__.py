
# pyright: reportUnusedImport=false
# ruff: noqa: F401

# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any, cast

import stouputils as stp
from beet import Context, Dialog, DialogTag, FormatSpecifier, Pack
from beet.core.utils import TextComponent, split_version
from box import Box
from stouputils.typing import JsonDict

from ...core import LATEST_MC_VERSION, MORE_ASSETS_PACK_FORMATS, MORE_DATA_PACK_FORMATS, MORE_DATA_VERSIONS, Mem, set_json_encoder
from ...dependencies.official_libs import OFFICIAL_LIBS
from ...telemetry import Telemetry
from ..copy_to_destination.sftp import SftpPool
from ..livereload import patch_livereload_for_copy_destinations
from .beet_patches import apply_beet_patches
from .project_images import find_pack_png
from .source_lore_font import SPACER_CHAR, TOOLTIP_FONT, prepare_source_lore_font, warn_foreign_tooltip_font

# Constants
TEXTURE_SUFFIX_RENAMES: dict[str, str] = {
	"_off": "",
	"_down": "_bottom",
	"_up": "_top",
	"_north": "_front",
	"_south": "_back",
	"_west": "_left",
	"_east": "_right",
}
""" Texture name parts renamed to the side names the generated models look for. """

PACK_KEYS_ORDER: tuple[str, ...] = ("pack_format", "description", "supported_formats", "min_format", "max_format")
""" The keys of `pack.mcmeta`'s `pack` that come first, in this order. """


# Main entry point
def beet_default(ctx: Context, silent: bool = False) -> Generator[None]:
	# The timer runs either way: `silent` only decides whether the line is printed,
	# and the telemetry event at the bottom needs the same duration the line would have shown.
	printer: Callable[..., None] = (lambda *_: None) if silent else stp.debug
	with stp.MeasureTime(print_func=printer, message="Total execution time") as time_ctx:

		# Monkey patch beet before anything walks a directory or saves a pack (see beet_patches)
		apply_beet_patches()
		assert ctx.project_id, "Project ID must be set in the project configuration."
		reset_build_state(ctx)

		# Enable livereload through `build_copy_destinations` if beet.contrib.livereload is used (no `beet link` needed)
		patch_livereload_for_copy_destinations(ctx)

		# Shake hands with the remote destinations while the build runs, so the copy plugin finds an open connection
		SftpPool.warmup_from_context(ctx)

		fill_defaults(ctx)
		object.__setattr__(ctx, "output_directory", stp.relative_path(str(Mem.ctx.output_directory)))
		register_pack_formats(ctx)
		rename_textures(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))

		# Extend the datapack namespace with sorter files
		ctx.require("stewbeet.plugins.datapack.sorters.extend_datapack")
		setup_pack_mcmeta(ctx, ctx.data, ctx.data.pack_format)
		setup_pack_mcmeta(ctx, ctx.assets, ctx.assets.pack_format)

		# Yield message to indicate successful build
		yield
		Telemetry.record_build((time_ctx.ns() - time_ctx.start_ns) / 1_000_000_000)


# Functions
def reset_build_state(ctx: Context) -> None:
	""" Start the build from empty memory, so consecutive builds in one process (`stewbeet watch`) behave like fresh runs.

	`ctx.meta` becomes a default Box, which every later plugin reads through.
	"""
	meta_box: Box = Box(ctx.meta, default_box=True, default_box_attr={})
	object.__setattr__(ctx, "meta", meta_box) # Bypass FrozenInstanceError
	Mem.ctx = ctx
	Mem.definitions = {}
	Mem.external_definitions = {}
	Mem.used_textures = set()
	Mem.text_renders = None

	stp.clear_simple_caches()
	from ..auto.lang_file.utils import lang
	lang.clear()
	from ...dependencies.download_manager import BUILD_CACHE
	BUILD_CACHE.clear()
	for data in OFFICIAL_LIBS.values():
		data["is_used"] = False


def fill_defaults(ctx: Context) -> None:
	""" Fill in the project description, the source lore and the manual name when the project leaves them out or sets "auto". """
	project_description: TextComponent = Mem.ctx.project_description
	if not project_description or project_description == "auto":
		object.__setattr__(Mem.ctx, "project_description", f"{ctx.project_name} [{ctx.project_version}] by {ctx.project_author}")

	source_lore: TextComponent = Mem.ctx.meta.get("stewbeet", {}).get("source_lore", "")
	if not source_lore or source_lore == "auto":
		# The project name is rendered with the tooltip font, prefixed by the logo glyph when there is a pack.png
		name: JsonDict = {"text": ctx.project_name, "italic": False, "color": "white", "font": f"{ctx.project_id}:{TOOLTIP_FONT}"}
		if not find_pack_png():
			Mem.ctx.meta["stewbeet"]["source_lore"] = [name]
		else:
			Mem.ctx.meta["stewbeet"]["source_lore"] = [{"text":"ICON"}, {**name, "text": f"{SPACER_CHAR}{ctx.project_name}"}]
	warn_foreign_tooltip_font(Mem.ctx.meta.get("stewbeet", {}).get("source_lore", []))
	Mem.ctx.meta["stewbeet"]["pack_icon_path"] = prepare_source_lore_font(Mem.ctx.meta.get("stewbeet", {}).get("source_lore", []))

	manual_name: TextComponent = Mem.ctx.meta.get("stewbeet", {}).get("manual", {}).get("name", "")
	if not manual_name:
		Mem.ctx.meta["stewbeet"]["manual"]["name"] = f"{ctx.project_name} Manual"


def register_pack_formats(ctx: Context) -> None:
	""" Teach beet the pack formats and data versions it does not know yet, and set both packs' format from the Minecraft version. """
	ctx.data.pack_format_registry.update(MORE_DATA_PACK_FORMATS)  # pyright: ignore[reportArgumentType, reportCallIssue]
	ctx.assets.pack_format_registry.update(MORE_ASSETS_PACK_FORMATS)  # pyright: ignore[reportArgumentType, reportCallIssue]
	ctx.meta["data_version"] = MORE_DATA_VERSIONS
	if ctx.minecraft_version:
		tuple_version: tuple[int, ...] = tuple(int(x) for x in ctx.minecraft_version.split(".") if x.isdigit())
		ctx.data.pack_format = ctx.data.pack_format_registry.get(tuple_version, ctx.data.pack_format)  # pyright: ignore[reportAttributeAccessIssue]
		ctx.assets.pack_format = ctx.assets.pack_format_registry.get(tuple_version, ctx.assets.pack_format)  # pyright: ignore[reportAttributeAccessIssue]


def rename_textures(textures_folder: str) -> None:
	""" Lowercase the textures at the top of the folder, with the side names of `TEXTURE_SUFFIX_RENAMES`, never overwriting. """
	if not textures_folder or not Path(textures_folder).exists():
		return
	for file in [f for f in os.listdir(textures_folder) if f.endswith(('.png', '.jpg', '.jpeg', ".mcmeta"))]:
		new_name: str = file.lower()
		for k, v in TEXTURE_SUFFIX_RENAMES.items():
			if k in file:
				new_name = new_name.replace(k, v)
		old_path: Path = Path(textures_folder) / file
		new_path: Path = Path(textures_folder) / new_name
		if new_name != file and old_path.exists() and not new_path.exists():
			os.rename(old_path, new_path)
			stp.warning(f"Renamed texture '{file}' to '{new_name}'")


def setup_pack_mcmeta(ctx: Context, pack: Pack[Any], pack_format: FormatSpecifier | None) -> None:
	""" Write a pack's `pack.mcmeta` over the one it has: its format, the range `mc_supports` gives, the description and the id.

	The format defaults to the Minecraft version's, else the latest known one's.
	"""
	if not pack_format:
		pack_format =  pack.pack_format_registry[(split_version(ctx.minecraft_version or LATEST_MC_VERSION))]
	existing_mcmeta: JsonDict = pack.mcmeta.data or {}
	pack_mcmeta: JsonDict = {"pack": {}}
	int_pack_format = pack_format if isinstance(pack_format, int) else pack_format[0]
	pack_mcmeta.update(existing_mcmeta)
	pack_mcmeta["pack"].update(existing_mcmeta.get("pack", {}))
	pack_mcmeta["pack"]["pack_format"] = int_pack_format

	# Formats from which min_format and max_format exist
	if (pack is ctx.data and (int_pack_format >= 82)) or (pack is ctx.assets and int_pack_format >= 65):
		pack_mcmeta["pack"]["min_format"] = pack_format
		pack_mcmeta["pack"]["max_format"] = 1000 if isinstance(pack_format, int) else (1000, 0)
	pack_mcmeta["pack"].update(supported_formats(ctx, pack, int_pack_format))
	pack_mcmeta["pack"]["description"] = Mem.ctx.project_description

	ordered_pack: JsonDict = {key: pack_mcmeta["pack"][key] for key in PACK_KEYS_ORDER if key in pack_mcmeta["pack"]}
	ordered_pack.update({k: v for k, v in pack_mcmeta["pack"].items() if k not in ordered_pack})
	pack_mcmeta["pack"] = ordered_pack
	pack_mcmeta["id"] = Mem.ctx.project_id
	pack.mcmeta.data = pack_mcmeta
	pack.mcmeta.encoder = lambda x: stp.json_dump(x, max_level=3)


def supported_formats(ctx: Context, pack: Pack[Any], int_pack_format: int) -> JsonDict:
	""" The formats a pack supports, from the first and last versions of `mc_supports`, empty when the project gives none.

	The first is capped at the project's Minecraft version, and "infinite" stands for it first and for the latest known one last.
	"""
	mc_supports = ctx.meta.get("mc_supports", [])
	if not isinstance(mc_supports, list) or not mc_supports:
		return {}
	mc_supports = cast(list[str], mc_supports)
	current: tuple[int, ...] = split_version(ctx.minecraft_version or LATEST_MC_VERSION)
	min_version: tuple[int, ...] = min(split_version(mc_supports[0]) if mc_supports[0] != "infinite" else current, current)
	latest: tuple[int, ...] = max(MORE_DATA_PACK_FORMATS.keys())
	max_version: tuple[int, ...] = split_version(mc_supports[-1]) if mc_supports[-1] != "infinite" else latest
	formats: JsonDict = {
		"min_format": pack.pack_format_registry.get(min_version, int_pack_format),
		"max_format": pack.pack_format_registry.get(max_version, int_pack_format),
	}
	if isinstance(formats["min_format"], int):
		max_format: FormatSpecifier = formats["max_format"]
		formats["supported_formats"] = [formats["min_format"], max_format if isinstance(max_format, int) else max_format[0]]
	return formats

