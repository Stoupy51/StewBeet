
# Imports
import os

from stouputils.continuous_delivery.cd_utils import handle_response, load_credentials  # noqa: F401

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
	supported_versions: list[str] = [version]
	if version == "1.21.3":
		supported_versions.append("1.21.2")
	return supported_versions

