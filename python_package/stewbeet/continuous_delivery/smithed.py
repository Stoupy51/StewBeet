
# ruff: noqa: E501
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
import os
import re
from typing import Any

import requests
import stouputils as stp
from stouputils.typing import JsonDict

from .cd_utils import get_supported_versions

# Constants
SMITHED_API_URL: str = "https://api.smithed.dev/v2/packs"

def validate_credentials(credentials: JsonDict) -> tuple[str, str]:
	""" Get and validate Smithed credentials

	Args:
		credentials: Credentials for the Smithed API
	Returns:
		str: API key for Smithed
		str: GitHub author
	"""
	if "smithed_api_key" not in credentials:
		raise ValueError("The credentials file must contain a 'smithed_api_key' key, which is a token with 'WRITE_PACKS' scope for the Smithed API: https://smithed.net/settings?tab=account")
	if "github" not in credentials:
		raise ValueError("The credentials file must contain a 'github' key, which is a dictionary containing a 'api_key' key (a PAT for the GitHub API: https://github.com/settings/tokens) and a 'username' key (the username of the account to use)")
	if "api_key" not in credentials["github"]:
		raise ValueError("The credentials file must contain a 'github' key, which is a dictionary containing a 'api_key' key (a PAT for the GitHub API: https://github.com/settings/tokens) and a 'username' key (the username of the account to use)")
	if "username" not in credentials["github"]:
		raise ValueError("The credentials file must contain a 'github' key, which is a dictionary containing a 'api_key' key (a PAT for the GitHub API: https://github.com/settings/tokens) and a 'username' key (the username of the account to use)")
	return credentials["smithed_api_key"], credentials["github"]["username"]

def validate_config(smithed_config: dict[str, Any]) -> tuple[str, str, str]:
	""" Validate Smithed configuration

	Args:
		smithed_config: Configuration for the Smithed project
	Returns:
		str: Project name on Smithed
		str: Version of the project
		str: Slug (namespace) of the project
	"""
	required_keys = ["project_id", "project_name", "version"]
	error_messages = {
		"project_id": "namespace of the project",
		"project_name": "name of the project on Smithed",
		"version": "version of the project",
	}

	for key in required_keys:
		if key not in smithed_config:
			raise ValueError(f"The smithed_config dictionary must contain a '{key}' key, which is the {error_messages[key]}")

	files: dict[str, str] | None = smithed_config.get("files")
	if files is not None:
		if "datapack" not in files or not set(files) <= {"datapack", "resourcepack"}:
			raise ValueError("The 'files' configuration of smithed_config must have a 'datapack' path and optionally a 'resourcepack' path")
		for path in files.values():
			if not os.path.isfile(path):
				raise FileNotFoundError(f"Configured Smithed file does not exist: {path}")
			if not re.fullmatch(r"[A-Za-z0-9._-]+", os.path.basename(path)):
				raise ValueError(f"The name of {path} must only hold letters, digits, '.', '_' and '-', as GitHub renames other release assets")

	return (
		smithed_config["project_id"],
		smithed_config["project_name"].replace(" ", ""),
		smithed_config["version"]
	)

def upload_version(
	project_id: str,
	project_name: str,
	version: str,
	api_key: str,
	author: str,
	files: dict[str, str] | None = None,
	github_project_name: str | None = None,
) -> None:
	""" Upload new version

	Args:
		project_id:          Smithed project ID
		project_name:        Name of the project
		version:             Version number
		api_key:             API key for Smithed
		author:              Author (for the github link)
		files:               Local 'datapack' and optional 'resourcepack' zips, already uploaded to the GitHub release
		github_project_name: GitHub repository name, if different from project_name
	"""
	stp.progress(f"Creating version {version}")
	post_url: str = f"{SMITHED_API_URL}/{project_id}/versions"
	repository_name: str = github_project_name or project_name
	data: JsonDict = {
		"name": version,
		"downloads": {},
		"supports": [
			# Exclude snapshot and release candidate versions (keep only numeric versions)
			x for x in get_supported_versions()
			if all(c in "0123456789." for c in x)
		],
		"dependencies": []
	}

	# Add the download links
	release_url: str = f"https://github.com/{author}/{repository_name}/releases/download/v{version}"
	candidates: dict[str, list[str]] = (
		{key: [f"{release_url}/{os.path.basename(path)}"] for key, path in files.items()} if files is not None else
		{
			"datapack":     [f"{release_url}/{project_name}_datapack_with_libs.zip", f"{release_url}/{project_name}_datapack.zip"],
			"resourcepack": [f"{release_url}/{project_name}_resource_pack_with_libs.zip", f"{release_url}/{project_name}_resource_pack.zip"],
		}
	)
	for key, urls in candidates.items():
		if url := next((url for url in urls if requests.get(url).status_code == 200), None):
			data["downloads"][key] = url

	response = requests.post(
		post_url,
		headers = {"Content-Type": "application/json"},
		params = {"token": api_key, "version": version},
		data = json.dumps({"data": data})
	)
	stp.handle_response(response, "Failed to create version on Smithed")


@stp.measure_time(message="Uploading to smithed took")
@stp.handle_error(error_log=stp.LogLevels.WARNING_TRACEBACK)
def upload_to_smithed(credentials: dict[str, str], smithed_config: dict[str, Any], changelog: str = "") -> None:
	""" Upload the project to Smithed using the credentials and the configuration

	Args:
		credentials:    Credentials for the Smithed API
		smithed_config: Configuration for the Smithed project
		changelog:      Changelog text for the release
	"""
	api_key, author = validate_credentials(credentials)
	project_id, project_name, version = validate_config(smithed_config)

	files: dict[str, str] | None = smithed_config.get("files")
	github_project_name: str | None = smithed_config.get("github_project_name")
	upload_version(project_id, project_name, version, api_key, author, files, github_project_name)

	stp.info(f"Project {project_name} updated on Smithed!")

