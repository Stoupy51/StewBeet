
# Imports
import re
from re import Pattern
from typing import Any

import stouputils as stp

from ..utils.io import FILES_TO_WRITE


def main(config: dict[str, Any]) -> None:
	""" Check for unused textures in the resource pack.

	Args:
		config (dict[str, Any]): Configuration containing:
			- "textures_files": list[str] of all texture filenames (e.g. ["dirt.png", "stone.png", ...])
			- "assets_folder": base path to the assets folder (e.g. "my_pack/assets/")
	"""
	# 1) Build a set of all texture names (without ".png"):
	all_textures: set[str] = {fname.rsplit(".png", 1)[0] for fname in config["textures_files"]}

	# 2) Concatenate all JSON contents into one big string:
	all_json_content: str = " ".join(
		content
		for path, content in FILES_TO_WRITE.items()
		if path.endswith(".json")
	)

	# 3) Run a single regex to extract ANY substring that looks like '/<texture>' or ':<texture>'
	#    followed by either ".png" or a closing quote ".
	#    This regex will catch both:
	#       "/dirt.png"
	#       ":stone"
	#       "/subfolder/brick.png"  (we'll strip off directories later)
	#
	#    Breakdown of the pattern:
	#      (?:(?:/|:))       → match either '/' or ':' but don't capture it
	#      (                  → start capturing group #1
	#          [^/:"\\]+      →  one or more chars that are NOT '/', ':', '"', or backslash
	#      )                  → end capturing group
	#      (?=\.png|" )       → lookahead: next char must be either ".png" or a double-quote
	#
	#    In practice, if your JSON references look like "/namespace:texture_name" or "modid:foo/bar/baz",
	#    you may need to tweak the class [^/:"\\]+ to include forward slashes. Here, we assume your
	#    texture references do NOT include subdirectories. If they DO, see the "Note on subfolders" below.
	texture_ref_regex: Pattern[str] = re.compile(r'(?:(?:/|:))([^/:"\\]+)(?=\.png|")')

	found_matches: set[str] = set(texture_ref_regex.findall(all_json_content))

	# 4) Now finally compute unused:
	unused_textures: set[str] = all_textures.difference(found_matches)

	# 5) If anything is unused, warn about it:
	if unused_textures:
		sorted_unused: list[str] = sorted(unused_textures)
		unused_paths: list[str] = [
			f"{config['assets_folder']}/textures/{name}.png"
			for name in sorted_unused
		]
		warning_lines: list[str] = [
			f"'{stp.relative_path(path)}' not used in the resource pack"
			for path in unused_paths
		]
		warning_msg: str = (
			"Some textures are not used in the resource pack:\n"
			+ "\n".join(warning_lines)
		)
		stp.warning(warning_msg)

