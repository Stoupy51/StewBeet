
# Imports
import os
from pathlib import Path

from beet import Context, Pack
from beet.core.utils import JsonDict, TextComponent
from box import Box
from stouputils import relative_path
from stouputils.decorators import measure_time
from stouputils.io import super_json_dump
from stouputils.print import warning

from ...core import Mem
from .source_lore_font import make_source_lore_font


# Main entry point
@measure_time(message="Total execution time")
def beet_default(ctx: Context):

	# Assertions
	assert ctx.project_id, "Project ID must be set in the project configuration."

	# Store the Box object in ctx for access throughout the codebase
	meta_box: Box = Box(ctx.meta, default_box=True, default_box_attr={})
	object.__setattr__(ctx, "meta", meta_box) # Bypass FrozenInstanceError
	Mem.ctx = ctx

	# Preprocess project description
	project_description: TextComponent = Mem.ctx.meta.stewbeet.project_description
	if not project_description or project_description == "auto":
		# Use project name, version, and author to create a default description
		Mem.ctx.meta.stewbeet.project_description = f"{ctx.project_name} [{ctx.project_version}] by {ctx.project_author}"

	# Preprocess source lore
	source_lore: TextComponent = Mem.ctx.meta.stewbeet.source_lore
	if not source_lore or source_lore == "auto":
		Mem.ctx.meta.stewbeet.source_lore = [{"text":"ICON"},{"text":f" {ctx.project_name}","italic":True,"color":"blue"}]
	make_source_lore_font(Mem.ctx.meta.stewbeet.source_lore)

	# Preprocess manual name
	manual_name: TextComponent = Mem.ctx.meta.stewbeet.manual.name
	if not manual_name:
		Mem.ctx.meta.stewbeet.manual.name = f"{ctx.project_name} Manual"

	# Convert paths to relative ones
	object.__setattr__(ctx, "output_directory", relative_path(Mem.ctx.output_directory))

	# Helper function to setup pack.mcmeta
	def setup_pack_mcmeta(pack: Pack, pack_format: int):
		existing_mcmeta = pack.mcmeta.data or {}
		pack_mcmeta: JsonDict = {"pack": {}}
		pack_mcmeta.update(existing_mcmeta)
		pack_mcmeta["pack"].update(existing_mcmeta.get("pack", {}))
		pack_mcmeta["pack"]["pack_format"] = pack_format
		pack_mcmeta["pack"]["description"] = Mem.ctx.meta.stewbeet.project_description
		pack_mcmeta["id"] = Mem.ctx.project_id
		pack.mcmeta.data = pack_mcmeta
		pack.mcmeta.encoder = super_json_dump

	# Setup pack.mcmeta for both packs
	setup_pack_mcmeta(ctx.data, ctx.data.pack_format)
	setup_pack_mcmeta(ctx.assets, ctx.assets.pack_format)

	# Convert texture names if needed (from old legacy system)
	textures_folder = Mem.ctx.meta.stewbeet.get("textures_folder")
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
					warning(f"Renamed texture {file} to {new_name}")

	# Yield message to indicate successful build
	yield

