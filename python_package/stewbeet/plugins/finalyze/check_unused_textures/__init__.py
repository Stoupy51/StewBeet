
# Imports
import os
from pathlib import Path
from typing import Any, cast

import stouputils as stp
from beet import Context, Texture
from stouputils.typing import JsonDict


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.finalyze.check_unused_textures'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the check unused textures plugin.
	This plugin checks for unused textures in the resource pack by analyzing all JSON files
	and comparing texture references with the available texture files.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	stewbeet: JsonDict = ctx.meta.get("stewbeet", {})
	textures_folder: str = stp.clean_path(stewbeet.get("textures_folder", ""))
	assert textures_folder, "meta.stewbeet.textures_folder is not set. Please set it in the project configuration."

	# 1) Build a dict of all textures file paths relative to the textures folder:
	# Ex: {'some_folder/dirt.png', 'stone.png', ...}
	textures: set[str] = {stp.relative_path(str(p), textures_folder) for p in Path(textures_folder).rglob("*.png")}

	# 2) For each texture, check if any of the ctx.assets.textures matches the texture filename.
	unused_paths: set[str] = set()
	for path in textures:
		# Get just the filename without extension for comparison
		filename_no_ext: str = os.path.splitext(os.path.basename(path))[0]
		no_extension_path: str = os.path.splitext(path)[0]
		if not any(
			(str(texture.source_path).endswith(no_extension_path) or filename_no_ext in str(texture.source_path)) if isinstance(texture, Texture)
			else (
				(texture.endswith(no_extension_path) or filename_no_ext in texture) if isinstance(texture, str)
				else False
			)
			for texture in cast(list[Any], ctx.assets.textures)
		):
			unused_paths.add(path)

	# 3) If anything is unused, warn about it:
	if unused_paths:
		warning_lines: list[str] = [
			f"- '{textures_folder}/{path}'"
			for path in sorted(unused_paths)
		]
		warning_msg: str = (
			"Some textures are not used in the resource pack:\n"
			+ "\n".join(warning_lines)
		)
		stp.warning(warning_msg)

