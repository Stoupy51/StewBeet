
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import fnmatch
import os
import re
from collections import defaultdict

import stouputils as stp
from beet import Context, Sound
from beet.core.utils import JsonDict
from mutagen.oggvorbis import OggVorbis

from ....core.utils.sounds import add_sound


# Main entry point
@stp.measure_time(message="Execution time of 'stewbeet.plugins.resource_pack.sounds'")
def beet_default(ctx: Context):
	""" Main entry point for the sounds plugin, generating sounds.json from the sounds folder.

	For instance, given a sounds folder structure like::

		sounds/
		├── dirt_bullet_impact_01.ogg
		├── dirt_bullet_impact_02.ogg
		├── dirt_bullet_impact_03.ogg
		└── fireselect.ogg

	The plugin will:
	- Group numbered variants (e.g. dirt_bullet_impact_01, dirt_bullet_impact_02, dirt_bullet_impact_03)
	- Process individual sounds (e.g. fireselect)
	- Generate the appropriate sounds.json configuration
	"""
	sounds_folder, exclude_patterns = sounds_settings(ctx.meta.get("stewbeet", {}))
	all_files: list[str] = sorted(os.path.join(root, file) for root, _, files in os.walk(sounds_folder) for file in files)
	sounds_names: list[str] = [sound for sound in all_files if sound.endswith(".ogg")]
	if not sounds_names:
		return

	# Excluded patterns are matched against paths relative to the sounds folder
	sounds_names = [
		s for s in sounds_names
		if not any(fnmatch.fnmatch(stp.relative_path(s, sounds_folder), pattern) for pattern in exclude_patterns)
	]
	for base_name, variants in sorted(group_variants(sounds_names, sounds_folder).items()):
		sounds: dict[str, Sound] = {
			os.path.splitext(variant)[0].lower().replace(" ", "_"): variant_sound(sounds_folder, variant)
			for variant in sorted(variants)
		}
		add_sound(ctx, sounds, base_name)


def sounds_settings(stewbeet_meta: JsonDict) -> tuple[str, list[str]]:
	""" The sounds folder and the patterns excluded from it, from `meta.stewbeet.sounds`.

	The deprecated `meta.stewbeet.sounds_folder` is still read, with a warning and nothing excluded.
	"""
	sounds_config: JsonDict | None = stewbeet_meta.get("sounds", None)
	if isinstance(sounds_config, dict) and sounds_config.get("folder"):
		return stp.relative_path(sounds_config["folder"]), sounds_config.get("exclude_patterns", [])
	old_sounds_folder: str = stewbeet_meta.get("sounds_folder", "")
	assert old_sounds_folder != "", (
		"Sounds folder path not found. Please set 'meta.stewbeet.sounds.folder' in project configuration."
	)
	stp.warning(
		"'meta.stewbeet.sounds_folder' is deprecated. "
		"Please migrate to 'meta.stewbeet.sounds.folder' instead. "
		"(See https://stewbeet.paralya.fr/markdown?src=plugins/resource_pack.sounds.md)"
	)
	return stp.relative_path(old_sounds_folder), []


def group_variants(sounds_names: list[str], sounds_folder: str) -> dict[str, list[str]]:
	""" Sound files grouped by name, numbered variants (`name_01`, `name2`) under their shared name.

	Each name is simplified to lowercase letters, digits, `.`, `_` and `/`, and the files are given relative to the folder.
	"""
	sound_groups: dict[str, list[str]] = defaultdict(list)
	for sound in sounds_names:
		rel_sound: str = stp.relative_path(sound, sounds_folder)
		sound_file: str = "".join(char for char in rel_sound.replace(" ", "_").lower() if char.isalnum() or char in "._/")
		sound_file_no_ext: str = os.path.splitext(sound_file)[0]
		base_name_match = re.match(r'(.+?)(?:_)?(\d+)$', sound_file_no_ext)
		if base_name_match:
			sound_groups[base_name_match.group(1)].append(rel_sound)
		else:
			sound_groups[sound_file_no_ext] = [rel_sound]
	return sound_groups


def variant_sound(sounds_folder: str, variant: str) -> Sound:
	""" One variant's sound, streamed when longer than 10 seconds, its subtitle the name without the trailing number. """
	subtitle: str = re.sub(r'[_\s]*\d+$', '', os.path.splitext(variant)[0]).strip()
	source_path: str = stp.clean_path(f"{sounds_folder}/{variant}")
	try:
		audio = OggVorbis(source_path)
		stream = audio.info and audio.info.length > 10.0
	except Exception:
		stream = False
	if stream:
		return Sound(source_path=source_path, subtitle=subtitle, stream=True)
	return Sound(source_path=source_path, subtitle=subtitle)

