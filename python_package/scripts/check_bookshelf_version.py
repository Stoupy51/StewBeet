""" Script to check if a new Bookshelf version is available.

This script checks the current installed Bookshelf version against the latest
available version and outputs 'true' if an update is available.

Returns:
	str: 'true' if an update is available, 'false' otherwise
"""

# Imports
import json
import os
from typing import Any

import requests
from on_bookshelf_release import API_URL, CONFIG_PATH
from stouputils.decorators import handle_error
from stouputils.print import warning


def load_current_version() -> str | None:
	""" Load the current Bookshelf version from config.

	Returns:
		str | None: The current version or None if not found
	"""
	if not os.path.exists(CONFIG_PATH):
		return None

	try:
		with open(CONFIG_PATH) as f:
			config: dict[str, Any] = json.load(f)
			return config.get("version")
	except (json.JSONDecodeError, FileNotFoundError) as e:
		warning(f"Failed to load current version: {e}")
		return None


def get_latest_version() -> str | None:
	""" Fetch the latest Bookshelf version from the API.

	Returns:
		str | None: The latest version or None if request failed
	"""
	try:
		response: requests.Response = requests.get(API_URL)
		response.raise_for_status()
		data: dict[str, Any] = response.json()
		# Assuming the version is in the tag_name field
		return data.get("tag_name", "")
	except (requests.RequestException, json.JSONDecodeError) as e:
		warning(f"Failed to fetch latest version: {e}")
		return None


@handle_error()
def main() -> None:
	""" Main function that checks for updates and prints result. """
	current_version: str | None = load_current_version()
	latest_version: str | None = get_latest_version()

	# If versions are different, an update is available, return true
	if latest_version is not None and current_version != latest_version:
		print("true")
	else:
		print("false")


if __name__ == "__main__":
	main()

