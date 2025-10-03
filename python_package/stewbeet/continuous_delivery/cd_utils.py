
# Imports
import os

from stouputils.continuous_delivery.cd_utils import load_credentials  # type: ignore # noqa: F401

from ..core.constants import MINECRAFT_VERSION


# Function that replace the "~" by the user's home directory
def replace_tilde(path: str) -> str:
	return path.replace("~", os.path.expanduser("~"))

# Supported versions
def get_supported_versions(version: str = MINECRAFT_VERSION) -> list[str]:
	""" Get the supported versions for a given version of Minecraft

	Args:
		version (str): Version of Minecraft
	Returns:
		list[str]: List of supported versions, ex: ["1.21.3", "1.21.2"]
	"""
	sames: list[list[str]] = [
		["1.21", "1.21", "1.21.1"],
		["1.21.2", "1.21.3"],
		["1.21.6", "1.21.7", "1.21.8"],
		["1.21.9", "1.21.10"],
	]
	for s in sames:
		if version in s:
			return s
	return [version]

