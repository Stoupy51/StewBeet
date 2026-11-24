
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import os
from pathlib import Path
from typing import TypeVar

import stouputils as stp
from beet import JsonFile, Texture

from ...__memory__ import Mem

# Constants
JsonFileT = TypeVar("JsonFileT", bound=JsonFile)


# Set the JSON encoder to json_dump for a JsonFile object
def set_json_encoder[JsonFileT: JsonFile](
	obj: JsonFileT, max_level: int | None = None, indent: str | int = '\t'
) -> JsonFileT:
	""" Set the encoder of the given object to json_dump

	Args:
		obj:       The object to set the encoder for
		max_level: The maximum level of the JSON dump, or None for default behavior
		indent:    The indentation character (default: '\t')
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
		source_path: The path to the texture (ex: "assets/textures/texture_name.png")
	Returns:
		Texture: The texture object
	"""
	mcmeta_path: str = f"{source_path}.mcmeta"
	if os.path.exists(mcmeta_path):
		return Texture(source_path=source_path, mcmeta=stp.json_load(mcmeta_path))
	return Texture(source_path=source_path)


def textures_folder() -> str:
	""" The project's ``meta.stewbeet.textures_folder``, relative to the working directory.

	Raises:
		AssertionError: When beet.yml sets no textures folder.
	"""
	folder: str = stp.relative_path(Mem.ctx.meta.get("stewbeet", {}).get("textures_folder", ""))
	assert folder != "", "Textures folder path not found in 'ctx.meta.stewbeet.textures_folder'. Set it in beet.yml."
	return folder


def source_textures() -> dict[str, str]:
	""" Every PNG of the textures folder and its subfolders, by file name (``steel_ingot.png``).

	The value is the path relative to the working directory. Of two files with the same name, the last in path order wins.
	"""
	return {path.name: stp.relative_path(str(path)) for path in sorted(Path(textures_folder()).rglob("*.png"), key=str)}

