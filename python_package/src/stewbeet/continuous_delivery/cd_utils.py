
# Imports
import json
import os

import requests
import stouputils as stp
import yaml

from ...stewbeet.core.constants import MINECRAFT_VERSION


# Function that replace the "~" by the user's home directory
def replace_tilde(path: str) -> str:
	return path.replace("~", os.path.expanduser("~"))

# Load credentials from file
@stp.handle_error(exceptions=(ValueError, FileNotFoundError))
def load_credentials(credentials_path: str) -> dict[str, str]:
	""" Load credentials from a JSON or YAML file into a dictionary

	The file must be in the following format (JSON example, you can imagine the YAML format):

	```json
	{
		"modrinth_api_key": "your_api_key_here",
		...
	}
	```

	Args:
		credentials_path (str): Path to the credentials file (.json or .yml)
	Returns:
		dict: Dictionary containing the credentials
	"""
	# Get the absolute path of the credentials file
	credentials_path = replace_tilde(credentials_path).replace("\\", "/")

	# Check if the file exists
	if not os.path.exists(credentials_path):
		raise FileNotFoundError(f"Credentials file not found at '{credentials_path}'")

	# Load the file if it's a JSON file
	if credentials_path.endswith('.json'):
		with open(credentials_path) as f:
			return json.load(f)

	# Else, load the file if it's a YAML file
	elif credentials_path.endswith(('.yml', '.yaml')):
		with open(credentials_path) as f:
			return yaml.safe_load(f)

	# Else, raise an error
	else:
		raise ValueError("Credentials file must be .json or .yml format")

# Handle a response
def handle_response(response: requests.Response, error_message: str) -> None:
	""" Handle a response from the API

	Args:
		response		(requests.Response): The response from the API
		error_message	(str): The error message to raise if the response is not successful
	"""
	if response.status_code < 200 or response.status_code >= 300:
		try:
			raise ValueError(f"{error_message}, response code {response.status_code} with response {response.json()}")
		except requests.exceptions.JSONDecodeError:
			raise ValueError(f"{error_message}, response code {response.status_code} with response {response.text}")  # noqa: B904

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

