
# Imports
from beet import Context, Sound, SoundConfig
from beet.core.utils import JsonDict
from stouputils.io import super_json_dump


# Functions
def add_sound(ctx: Context, sounds: Sound | dict[str, Sound], name: str, ns: str = ""):
	""" Add a sound to the resource pack.

	Args:
		ctx    (Context):                   The beet context.
		sounds (Sound | dict[str, Sound]):  The sound object(s) to add. Can be a single Sound or a dict mapping local names to Sounds.
		name   (str):                       The identifier used in /playsound command (excluding namespace)
		ns     (str):                       The namespace to write the sound to (defaults to ctx.project_id).
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
	config: JsonDict = ctx.assets[ns].sound_config.data

	# Copy the sounds to the resource pack
	for path, sound in sounds.items():
		ctx.assets[ns].sounds[path] = sound

	# Create a new sound config
	new_config: JsonDict = {name: {
		"subtitle": name.split("/")[-1],
		"sounds": [
			{
				"name": f"{ns}:{path}",
				**{k: v for k, v in {
					"volume": sound.volume,
					"pitch": sound.pitch,
					"weight": sound.weight,
					"stream": sound.stream,
					"attenuation_distance": sound.attenuation_distance,
					"preload": sound.preload,
				}.items() if v is not None}
			}
			if
				any(v is not None for v in [
					sound.volume,
					sound.pitch,
					sound.weight,
					sound.stream,
					sound.attenuation_distance,
					sound.preload,
				])
			else
				f"{ns}:{path}"
			for path, sound in sounds.items()]
	}}

	# Update the sound config
	config.update(new_config)
	ctx.assets[ns].sound_config = SoundConfig(super_json_dump(config))

