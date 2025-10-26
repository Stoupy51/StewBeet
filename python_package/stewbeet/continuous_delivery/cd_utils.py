
# Imports
import os

from stouputils.continuous_delivery.cd_utils import load_credentials  # type: ignore # noqa: F401

from ..core.constants import LATEST_MC_VERSION
from ..utils import ProjectConfig, get_project_config


# Function that replace the "~" by the user's home directory
def replace_tilde(path: str) -> str:
	return path.replace("~", os.path.expanduser("~"))

# Supported versions
def get_supported_versions(version: str | list[str] | None = None) -> list[str]:
	""" Get the supported versions for a given version of Minecraft

	Args:
		version (str): Version of Minecraft
	Returns:
		list[str]: List of supported versions, ex: ["1.21.3", "1.21.2"]
	"""
	# If version is None, get it from the project config, otherwise use the default version
	if version is None:
		try:
			config: ProjectConfig = get_project_config()
			version = config.meta.get("mc_supports") or config.minecraft or LATEST_MC_VERSION
		except AssertionError:
			version = LATEST_MC_VERSION
	if isinstance(version, list):
		return [x for x in version if x != "infinite"]
	version = str(version)

	# Some versions are considered the same for compatibility purposes
	sames: list[list[str]] = [
		["1.21", "1.21", "1.21.1"],
		["1.21.2", "1.21.3"],
		["1.21.6", "1.21.7", "1.21.8"],
		["1.21.9", "1.21.10"],
	]

	# Find the matching list of versions
	for s in sames:
		if version in s:
			return s

	# If no match, return the version itself in a list
	return [version]

