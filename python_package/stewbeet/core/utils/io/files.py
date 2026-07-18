
# Imports
import os
from typing import TypeVar

import stouputils as stp
from beet import JsonFile, Texture

# Constants
JsonFileT = TypeVar("JsonFileT", bound=JsonFile)


# Set the JSON encoder to json_dump for a JsonFile object
def set_json_encoder[JsonFileT: JsonFile](
	obj: JsonFileT, max_level: int | None = None, indent: str | int = '\t'
) -> JsonFileT:
	""" Set the encoder of the given object to json_dump

	Args:
		obj			(JsonFile):		The object to set the encoder for
		max_level	(int | None):	The maximum level of the JSON dump, or None for default behavior
		indent		(str | int):	The indentation character (default: '\t')
	Returns:
		JsonFile: The object with the encoder set
	"""
	if max_level is None:
		obj.encoder = lambda x: stp.json_dump(x, indent=indent)
	else:
		obj.encoder = lambda x: stp.json_dump(x, max_level=max_level, indent=indent)
	return obj


# Create a texture object with mcmeta if found
def texture_mcmeta(source_path: str) -> Texture:
	""" Create a Texture object with mcmeta if found

	Args:
		source_path (str): The path to the texture (ex: "assets/textures/texture_name.png")
	Returns:
		Texture: The texture object
	"""
	mcmeta_path: str = f"{source_path}.mcmeta"
	if os.path.exists(mcmeta_path):
		return Texture(source_path=source_path, mcmeta=stp.json_load(mcmeta_path))
	return Texture(source_path=source_path)
