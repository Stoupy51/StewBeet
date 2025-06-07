
# Imports
import os
import re
import time
from collections import defaultdict

import stouputils as stp

from ..utils.io import super_copy, write_file


def main(config: dict):
	sounds_folder: str = stp.clean_path(config.get("assets_folder", "") + "/sounds")
	if sounds_folder != "/sounds" and not os.path.exists(sounds_folder):
		return

	# Get all files
	all_files: list[str] = [stp.clean_path(f"{root}/{file}") for root, _, files in os.walk(sounds_folder) for file in files]
	sounds_names: list[str] = [sound for sound in all_files if sound.endswith(".ogg") or sound.endswith(".wav")]

	# Add the sounds folder to the resource pack
	if sounds_names:
		start_time: float = time.perf_counter()

		# Dictionary to group sound variants
		sound_groups: dict[str, list[str]] = defaultdict(list)

		def handle_sound(sound: str) -> None:
			rel_sound: str = sound.replace(sounds_folder + "/", "")

			# Get sound without spaces and special characters
			sound_file: str = "".join(char for char in rel_sound.replace(" ", "_") if char.isalnum() or char in "._/").lower()

			# Copy to resource pack
			super_copy(f"{sounds_folder}/{rel_sound}", f"{config['build_resource_pack']}/assets/{config['namespace']}/sounds/{sound_file}")

			# Get sound without file extension
			sound_file_no_ext: str = ".".join(sound_file.split(".")[:-1])

			# Check if sound is a numbered variant (e.g. name_01, name_02 or name1, name2)
			base_name_match = re.match(r'(.+?)(?:_)?(\d+)$', sound_file_no_ext)
			if base_name_match:
				base_name: str = base_name_match.group(1)
				sound_groups[base_name].append(sound_file_no_ext)
			else:
				# Not a numbered variant, add as individual sound
				sound_groups[sound_file_no_ext] = [sound_file_no_ext]

		# Process sounds in parallel
		stp.multithreading(handle_sound, sounds_names, max_workers=min(32, len(sounds_names)))

		# Create sounds.json with grouped sounds
		sounds_json: dict = {}
		for base_name, variants in sorted(sound_groups.items()):
			# Convert directory separators to dots for the sound ID
			sound_id: str = base_name

			if len(variants) > 1:
				# Multiple variants - group them
				sounds_json[sound_id] = {
					"subtitle": sound_id.split("/")[-1],
					"sounds": [f"{config['namespace']}:{variant}" for variant in sorted(variants)]
				}
			else:
				# Single sound
				sounds_json[sound_id] = {
					"subtitle": sound_id.split("/")[-1],
					"sounds": [f"{config['namespace']}:{variants[0]}"]
				}

		# Write the sounds.json file
		write_file(f"{config['build_resource_pack']}/assets/{config['namespace']}/sounds.json", stp.super_json_dump(sounds_json))

		total_time: float = time.perf_counter() - start_time
		stp.info(f"All sounds in '{stp.replace_tilde(sounds_folder)}/' have been copied to the resource pack in {total_time:.5f}s")


