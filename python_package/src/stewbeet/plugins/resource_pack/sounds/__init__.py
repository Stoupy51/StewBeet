
# Imports
import os
import re
from collections import defaultdict

from beet import Context, Sound
from stouputils.decorators import measure_time
from stouputils.io import clean_path, relative_path
from stouputils.parallel import multithreading
from stouputils.print import progress

from ....core.utils.sounds import add_sound


# Main entry point
@measure_time(progress, message="Execution time of 'stewbeet.plugins.resource_pack.sounds'")
def beet_default(ctx: Context):
	""" Main entry point for the sounds plugin.
	This plugin handles sound file processing and generation of sounds.json based of the sounds folder.

	For instance, given a sounds folder structure like:
	```
	sounds/
	├── dirt_bullet_impact_01.ogg
	├── dirt_bullet_impact_02.ogg
	├── dirt_bullet_impact_03.ogg
	└── fireselect.ogg
	```

	The plugin will:
	- Group numbered variants (e.g. dirt_bullet_impact_01, dirt_bullet_impact_02, dirt_bullet_impact_03)
	- Process individual sounds (e.g. fireselect)
	- Generate the appropriate sounds.json configuration

	Args:
		ctx (Context): The beet context.
	"""
	# Get sounds folder from meta
	sounds_folder: str = relative_path(ctx.meta.get("stewbeet", {}).get("sounds_folder", ""))
	assert sounds_folder != "", "Sounds folder path not found in 'ctx.meta.stewbeet.sounds_folder'. Please set a directory path in project configuration."

	# Get all sound files
	all_files: list[str] = [os.path.join(root, file) for root, _, files in os.walk(sounds_folder) for file in files]
	sounds_names: list[str] = [sound for sound in all_files if sound.endswith((".ogg", ".wav"))]
	if not sounds_names:
		return

	# Dictionary to group sound variants
	sound_groups: dict[str, list[str]] = defaultdict(list)

	def handle_sound(sound: str) -> None:
		""" Process a single sound file.

		Args:
			sound (str): Path to the sound file.
		"""
		# Get relative path from sounds folder, simplified name, and without extension
		rel_sound: str = relative_path(sound, sounds_folder)
		sound_file: str = "".join(char for char in rel_sound.replace(" ", "_").lower() if char.isalnum() or char in "._/")
		sound_file_no_ext: str = os.path.splitext(sound_file)[0]

		# Check if sound is a numbered variant (e.g. name_01, name_02 or name1, name2)
		base_name_match = re.match(r'(.+?)(?:_)?(\d+)$', sound_file_no_ext)
		if base_name_match:
			base_name: str = base_name_match.group(1)
			sound_groups[base_name].append(rel_sound)
		else:
			# Not a numbered variant, add as individual sound
			sound_groups[sound_file_no_ext] = [rel_sound]

	# Process sounds in parallel
	multithreading(handle_sound, sounds_names, max_workers=min(32, len(sounds_names)))

	# Create sounds using add_sound function
	for base_name, variants in sorted(sound_groups.items()):
		# Create a dictionary mapping variant names to Sound objects
		sounds: dict[str, Sound] = {}

		# Process each variant
		for variant in sorted(variants):
			# Get variant name without extension
			variant_name: str = os.path.splitext(variant)[0]

			# Create Sound object for this variant
			sounds[variant_name] = Sound(
				source_path=clean_path(f"{sounds_folder}/{variant}"),
				subtitle=base_name.split("/")[-1]
			)

		# Add all variants to the sound system
		add_sound(ctx, sounds, base_name)

