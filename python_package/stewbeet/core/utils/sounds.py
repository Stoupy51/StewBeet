
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
from typing import Any, cast

import stouputils as stp
from beet import Context, Sound, SoundConfig
from stouputils.typing import JsonDict


# Functions
def add_sound(ctx: Context, sounds: Sound | dict[str, Sound], name: str, ns: str = ""):
	""" Add a sound to the resource pack, ex: ``add_sound(ctx, Sound("path/to/sound.ogg"), "my_sound")``.

	Args:
		sounds: A single Sound, or a dict mapping local names to Sounds.
		name:   The identifier used in /playsound command (excluding namespace)
		ns:     The namespace to write the sound to (defaults to ctx.project_id).
	"""
	# Default namespace
	if not ns:
		ns = ctx.project_id

	# Convert sounds to a dict
	if isinstance(sounds, Sound):
		sounds = {name: sounds}

	# If sounds.json isn't created, create it
	if not ctx.assets[ns].extra.get("sounds.json"):
		ctx.assets[ns].sound_config = SoundConfig()
	config: JsonDict = ctx.assets[ns].sound_config.data  # pyright: ignore[reportOptionalMemberAccess]

	# Copy the sounds to the resource pack
	for path, sound in sounds.items():
		ctx.assets[ns].sounds[path] = sound

	# Create a new sound config
	# Use subtitle from the first sound if available, otherwise use the sound name
	first_sound = next(iter(sounds.values()))
	subtitle = first_sound.subtitle if first_sound.subtitle else name.split("/")[-1].replace("_", " ").title()

	new_config: JsonDict = {name: {
		"subtitle": subtitle,
		"sounds": [
			{
				"name": f"{ns}:{path}",
				**{k: v for k, v in cast(JsonDict, {
					"volume": sound.volume,
					"pitch": sound.pitch,
					"weight": sound.weight,
					"stream": sound.stream,
					"attenuation_distance": sound.attenuation_distance,
					"preload": sound.preload,
				}).items() if v is not None}
			}
			if
				any(v is not None for v in cast(list[Any], [
					sound.volume,
					sound.pitch,
					sound.weight,
					sound.stream,
					sound.attenuation_distance,
					sound.preload,
				]))
			else
				f"{ns}:{path}"
			for path, sound in sounds.items()]
	}}

	# Update the sound config
	config.update(new_config)
	ctx.assets[ns].sound_config = SoundConfig(stp.json_dump(config))

