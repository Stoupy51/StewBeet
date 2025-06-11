
# Imports
import os
from pathlib import Path

from beet import Context, Texture
from beet.core.utils import JsonDict
from stouputils.decorators import measure_time
from stouputils.io import clean_path, relative_path
from stouputils.print import progress, warning


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.finalyze.check_unused_textures'")
def beet_default(ctx: Context) -> None:
	""" Main entry point for the check unused textures plugin.
	This plugin checks for unused textures in the resource pack by analyzing all JSON files
	and comparing texture references with the available texture files.

	Args:
		ctx (Context): The beet context.
	"""
	# Assertions
	stewbeet: JsonDict = ctx.meta.get("stewbeet", {})
	textures_folder: str = clean_path(stewbeet.get("textures_folder", ""))
	assert textures_folder, "meta.stewbeet.textures_folder is not set. Please set it in the project configuration."

	# 1) Build a dict of all textures file paths relative to the textures folder:
	# Ex: {'some_folder/dirt.png', 'stone.png', ...}
	textures: set[str] = {relative_path(p, textures_folder) for p in Path(textures_folder).rglob("*.png")}

	# 2) For each texture, check if any of the ctx.assets.textures endswith the texture path.
	unused_paths: set[str] = set()
	for path in textures:
		no_extension_path: str = os.path.splitext(path)[0]
		if not any(
			texture.source_path.endswith(no_extension_path) if isinstance(texture, Texture)
			else (
				texture.endswith(no_extension_path) if isinstance(texture, str)
				else False
			)
			for texture in ctx.assets.textures
		):
			unused_paths.add(path)

	# 3) If anything is unused, warn about it:
	if unused_paths:
		warning_lines: list[str] = [
			f"'{textures_folder}/{path}' not used in the resource pack"
			for path in sorted(unused_paths)
		]
		warning_msg: str = (
			"Some textures are not used in the resource pack:\n"
			+ "\n".join(warning_lines)
		)
		warning(warning_msg)


