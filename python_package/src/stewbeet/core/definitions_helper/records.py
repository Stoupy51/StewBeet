
# Imports
import os
from string import ascii_lowercase, digits

from beet import JukeboxSong, Sound
from mutagen.oggvorbis import OggVorbis
from stouputils.decorators import handle_error
from stouputils.io import clean_path, super_json_dump
from stouputils.print import error, warning

from ..__memory__ import Mem
from ..constants import CATEGORY, CUSTOM_ITEM_VANILLA
from ..utils.sounds import add_sound


# Cleaning function
def clean_record_name(name: str) -> str:
    """ Clean a record name by removing special characters and converting to lowercase.

    Args:
        name (str): The name to clean

    Returns:
        str: The cleaned name containing only lowercase letters, numbers and underscores
    """
    name = name.replace(".ogg", "").lower()
    to_replace = [" ", "-", "___"]
    for r in to_replace:
        name = name.replace(r, "_")
    return "".join([c for c in name if c in ascii_lowercase + digits + "_"])


# Custom records
@handle_error
def generate_custom_records(records: dict[str, str] | str | None = "auto", category: str | None = None) -> None:
	""" Generate custom records by searching in assets/records/ for the files and copying them to the definitions and resource pack folder.

	Args:
		definitions	(dict[str, dict]):	The definitions to add the custom records items to, ex: {"record_1": "song.ogg", "record_2": "another_song.ogg"}
		records		(dict[str, str]):	The custom records to apply, ex: {"record_1": "My first Record.ogg", "record_2": "A second one.ogg"}
		category	(str):				The definitions category to apply to the custom records (ex: "music").
	"""
	# Assertions
	assert records is None or isinstance(records, dict) or records in ["auto", "all"], (
        f"Error during custom record generation: records must be a dictionary, 'auto', or 'all' (got {type(records).__name__})"
	)
	records_folder: str = clean_path(Mem.ctx.meta.get("stewbeet", {}).get("records_folder", ""))
	assert records_folder != "", "Records folder path not found in 'ctx.meta.stewbeet.records_folder'. Please set a directory path in project configuration."

	# If no records specified, search in the records folder
	if not records or records in ["auto", "all"]:
		songs: list[str] = [x for x in os.listdir(records_folder) if x.endswith((".ogg",".wav"))]
		records_to_check: dict[str, str] = { clean_record_name(file): file for file in songs }
	else:
		records_to_check = records # type: ignore

	# For each record, add it to the definitions
	for record, sound in records_to_check.items():
		# Validate sound file format
		if not isinstance(sound, str):
			error(f"Error during custom record generation: sound '{sound}' is not a string, got {type(sound).__name__}")
		if not sound.endswith(".ogg"):
			warning(f"Error during custom record generation: sound '{sound}' is not an ogg file")
			continue

		# Extract item name from sound file
		item_name: str = os.path.splitext(sound)[0]	# Remove the file extension

		# Create definitions entry for the record
		Mem.definitions[record] = {
			"id": CUSTOM_ITEM_VANILLA,
			"custom_data": {Mem.ctx.project_id:{record: True}, "smithed":{"dict":{"record": {record: True}}}},
			"item_name": {"text":"Music Disc", "italic": False},
			"jukebox_playable": f"{Mem.ctx.project_id}:{record}",
			"max_stack_size": 1,
			"rarity": "rare",
		}
		if category:
			Mem.definitions[record][CATEGORY] = category

		# Process sound file
		file_path: str = f"{records_folder}/{sound}"
		if os.path.exists(file_path):
			try:
				# Get song duration from Ogg file
				duration: int = round(OggVorbis(file_path).info.length) # type: ignore

				# Create and write jukebox song configuration
				json_song: dict = {
					"comparator_output": duration % 16,
					"length_in_seconds": duration + 1,
					"sound_event": {"sound_id":f"{Mem.ctx.project_id}:{record}"},
					"description": {"text": item_name}
				}
				Mem.ctx.data[f"{Mem.ctx.project_id}:{record}"] = JukeboxSong(super_json_dump(json_song))

				# Create and write sound
				add_sound(Mem.ctx, sounds=Sound(source_path=file_path, stream=True), name=record)

			except Exception as e:
				error(f"Error during custom record generation of '{file_path}', make sure it is using proper Ogg format: {e}")
		else:
			warning(f"Error during custom record generation: path '{file_path}' does not exist")

