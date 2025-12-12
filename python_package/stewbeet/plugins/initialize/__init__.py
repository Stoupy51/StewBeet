
# pyright: reportUnusedImport=false
# ruff: noqa: F401
# Imports
import os
from pathlib import Path
from typing import Any, cast

from beet import Context, Dialog, DialogTag, FormatSpecifier, Pack
from beet.core.utils import JsonDict, TextComponent, split_version
from box import Box
from stouputils import debug, relative_path
from stouputils.decorators import measure_time, retry
from stouputils.io import json_dump
from stouputils.print import warning

from ...core import LATEST_MC_VERSION, MORE_ASSETS_PACK_FORMATS, MORE_DATA_PACK_FORMATS, MORE_DATA_VERSIONS, Mem, set_json_encoder
from .source_lore_font import find_pack_png, prepare_source_lore_font


# Main entry point
@measure_time(printer=debug, message="Total execution time", is_generator=True)
def beet_default(ctx: Context):

	# Assertions
	assert ctx.project_id, "Project ID must be set in the project configuration."

	# Store the Box object in ctx for access throughout the codebase
	meta_box: Box = Box(ctx.meta, default_box=True, default_box_attr={}) # type: ignore
	object.__setattr__(ctx, "meta", meta_box) # Bypass FrozenInstanceError
	Mem.ctx = ctx

	# Preprocess project description
	project_description: TextComponent = Mem.ctx.project_description
	if not project_description or project_description == "auto":
		# Use project name, version, and author to create a default description
		object.__setattr__(Mem.ctx, "project_description", f"{ctx.project_name} [{ctx.project_version}] by {ctx.project_author}")

	# Preprocess source lore
	source_lore: TextComponent = Mem.ctx.meta.get("stewbeet", {}).get("source_lore", "")
	if not source_lore or source_lore == "auto":
		if not find_pack_png():
			Mem.ctx.meta["stewbeet"]["source_lore"] = [{"text": ctx.project_name,"italic":True,"color":"blue"}]
		else:
			Mem.ctx.meta["stewbeet"]["source_lore"] = [{"text":"ICON"},{"text":f" {ctx.project_name}","italic":True,"color":"blue"}]
	Mem.ctx.meta["stewbeet"]["pack_icon_path"] = prepare_source_lore_font(Mem.ctx.meta.get("stewbeet", {}).get("source_lore", []))

	# Preprocess manual name
	manual_name: TextComponent = Mem.ctx.meta.get("stewbeet", {}).get("manual", {}).get("name", "")
	if not manual_name:
		Mem.ctx.meta["stewbeet"]["manual"]["name"] = f"{ctx.project_name} Manual"

	# Convert paths to relative ones
	object.__setattr__(ctx, "output_directory", relative_path(str(Mem.ctx.output_directory)))

	# Add missing pack format registries if not present, and data version
	ctx.data.pack_format_registry.update(MORE_DATA_PACK_FORMATS)
	ctx.assets.pack_format_registry.update(MORE_ASSETS_PACK_FORMATS)
	ctx.meta["data_version"] = MORE_DATA_VERSIONS
	if ctx.minecraft_version:
		tuple_version: tuple[int, ...] = tuple(int(x) for x in ctx.minecraft_version.split(".") if x.isdigit())
		ctx.data.pack_format = ctx.data.pack_format_registry.get(tuple_version, ctx.data.pack_format) # type: ignore
		ctx.assets.pack_format = ctx.assets.pack_format_registry.get(tuple_version, ctx.assets.pack_format) # type: ignore

	# Convert texture names if needed (from old legacy system)
	textures_folder: str = Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", "")
	if textures_folder and Path(textures_folder).exists():
		REPLACEMENTS = {
			"_off": "",
			"_down": "_bottom",
			"_up": "_top",
			"_north": "_front",
			"_south": "_back",
			"_west": "_left",
			"_east": "_right",
		}

		# Get all texture files
		texture_files = [f for f in os.listdir(textures_folder) if f.endswith(('.png', '.jpg', '.jpeg', ".mcmeta"))]

		for file in texture_files:
			new_name = file.lower()
			for k, v in REPLACEMENTS.items():
				if k in file:
					new_name = new_name.replace(k, v)

			if new_name != file:
				old_path = Path(textures_folder) / file
				new_path = Path(textures_folder) / new_name
				if old_path.exists() and not new_path.exists():
					os.rename(old_path, new_path)
					warning(f"Renamed texture '{file}' to '{new_name}'")

	# Extend the datapack namespace with sorter files
	ctx.require("stewbeet.plugins.datapack.sorters.extend_datapack")

	# Helper function to setup pack.mcmeta
	def setup_pack_mcmeta(pack: Pack[Any], pack_format: FormatSpecifier | None) -> None:
		# Default to latest if not given
		if not pack_format:
			pack_format =  pack.pack_format_registry[(split_version(ctx.minecraft_version or LATEST_MC_VERSION))]

		# Setup pack.mcmeta data
		existing_mcmeta: JsonDict = pack.mcmeta.data or {}
		pack_mcmeta: JsonDict = {"pack": {}}

		# Determine int pack format
		int_pack_format = pack_format if isinstance(pack_format, int) else pack_format[0]

		# Update existing mcmeta data and set pack_format
		pack_mcmeta.update(existing_mcmeta)
		pack_mcmeta["pack"].update(existing_mcmeta.get("pack", {}))
		pack_mcmeta["pack"]["pack_format"] = int_pack_format

		# Set min and max pack formats (if applicable)
		if (pack is ctx.data and (int_pack_format >= 82)) or (pack is ctx.assets and int_pack_format >= 65):
			pack_mcmeta["pack"]["min_format"] = pack_format
			pack_mcmeta["pack"]["max_format"] = 1000 if isinstance(pack_format, int) else (1000, 0)

		# Set min and max data versions (if mc_supports given)
		mc_supports = ctx.meta.get("mc_supports", [])
		if isinstance(mc_supports, list):
			mc_supports = cast(list[str], mc_supports)
			if len(mc_supports) > 0:
				min_version: tuple[int, ...] = split_version(mc_supports[0] if mc_supports[0] != "infinite" else ctx.minecraft_version or LATEST_MC_VERSION)
				max_version: tuple[int, ...] = split_version(mc_supports[-1]) if mc_supports[-1] != "infinite" else max(MORE_DATA_PACK_FORMATS.keys())
				pack_mcmeta["pack"]["min_format"] = pack.pack_format_registry.get(min_version, int_pack_format)
				pack_mcmeta["pack"]["max_format"] = pack.pack_format_registry.get(max_version, int_pack_format)
				if isinstance(pack_mcmeta["pack"]["min_format"], int):
					max_format: FormatSpecifier = pack_mcmeta["pack"]["max_format"]
					int_max_format: int = max_format if isinstance(max_format, int) else max_format[0]
					pack_mcmeta["pack"]["supported_formats"] = [pack_mcmeta["pack"]["min_format"], int_max_format]

		# Set description and id
		pack_mcmeta["pack"]["description"] = Mem.ctx.project_description

		# Reorder pack keys
		ordered_pack: JsonDict = {}
		for key in ["pack_format", "description", "supported_formats", "min_format", "max_format"]:
			if key in pack_mcmeta["pack"]:
				ordered_pack[key] = pack_mcmeta["pack"][key]
		ordered_pack.update({k: v for k, v in pack_mcmeta["pack"].items() if k not in ordered_pack})
		pack_mcmeta["pack"] = ordered_pack

		# Set pack ID, use new pack_mcmeta, and set json encoder
		pack_mcmeta["id"] = Mem.ctx.project_id
		pack.mcmeta.data = pack_mcmeta
		pack.mcmeta.encoder = lambda x: json_dump(x, max_level=3)

	# Setup pack.mcmeta for both packs
	setup_pack_mcmeta(ctx.data, ctx.data.pack_format)
	setup_pack_mcmeta(ctx.assets, ctx.assets.pack_format)

	# Fix pack.save to retry when there is a PermissionError (for example, when vscode or another program locks a file temporarily)
	Pack.save = retry(Pack.save, exceptions=PermissionError, max_attempts=10, delay=1.0, backoff=1.2)  # type: ignore

	# # Setup dialog convention for pause screen additions
	# Mem.ctx.data["minecraft"].dialogs_tags["pause_screen_additions"] = set_json_encoder(DialogTag({"values":[{"id":"smithed:data_packs","required":False}]}))
	# Mem.ctx.data["smithed"].dialogs_tags["data_packs"] = set_json_encoder(DialogTag({"values":[]}))
	# Mem.ctx.data["smithed"].dialogs["data_packs"] = set_json_encoder(Dialog({
	# 	"type": "minecraft:dialog_list",
	# 	"external_title": {
	# 		"translate": "menu.smithed.data_packs",
	# 		"fallback": "%s...",
	# 		"with": [{"translate": "selectWorld.dataPacks"}]
	# 	},
	# 	"title": {
	# 		"translate": "menu.smithed.data_packs.title",
	# 		"fallback": "%s",
	# 		"with": [{"translate": "selectWorld.dataPacks"}]
	# 	},
	# 	"dialogs": "#smithed:data_packs",
	# 	"exit_action": {"label": {"translate": "gui.back"}, "width": 200}
	# }))

	# Yield message to indicate successful build
	yield

