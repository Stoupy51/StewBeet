
# ruff: noqa: E501
# Imports
import json

import requests
import stouputils as stp

from .cd_utils import get_supported_versions, handle_response

# Constants
SMITHED_API_URL: str = "https://api.smithed.dev/v2/packs"

def validate_credentials(credentials: dict) -> tuple[str, str]:
	""" Get and validate Smithed credentials

	Args:
		credentials (dict[str, str]): Credentials for the Smithed API
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

def validate_config(smithed_config: dict[str, str]) -> tuple[str, str, str]:
	""" Validate Smithed configuration

	Args:
		smithed_config (dict[str, str]): Configuration for the Smithed project
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

	return (
		smithed_config["project_id"],
		smithed_config["project_name"],
		smithed_config["version"]
	)

def upload_version(project_id: str, project_name: str, version: str, api_key: str, author: str) -> None:
	""" Upload new version

	Args:
		project_id		(str):				Smithed project ID
		project_name	(str):				Name of the project
		version			(str):				Version number
		api_key			(str):				API key for Smithed
		author			(str):				Author (for the github link)
	"""
	stp.progress(f"Creating version {version}")
	post_url: str = f"{SMITHED_API_URL}/{project_id}/versions"
	data: dict = {
		"name": version,
		"downloads": {},
		"supports": get_supported_versions(),
		"dependencies": []
	}

	# Add the download links
	links: dict[str, str] = {
		"datapack":			f"https://github.com/{author}/{project_name}/releases/download/v{version}/{project_name}_datapack_with_libs.zip",
		"resourcepack":		f"https://github.com/{author}/{project_name}/releases/download/v{version}/{project_name}_resource_pack_with_libs.zip"
	}
	for key, value in links.items():
		if requests.get(value).status_code == 200:
			data["downloads"][key] = value
		else:
			value = value.replace("_with_libs", "")
			if requests.get(value).status_code == 200:
				data["downloads"][key] = value

	response = requests.post(
		post_url,
		headers = {"Content-Type": "application/json"},
		params = {"token": api_key, "version": version},
		data = json.dumps({"data": data})
	)
	handle_response(response, "Failed to create version on Smithed")


@stp.measure_time(stp.progress, "Uploading to smithed took")
@stp.handle_error(error_log=stp.LogLevels.WARNING_TRACEBACK)
def upload_to_smithed(credentials: dict[str, str], smithed_config: dict, changelog: str = "") -> None:
	""" Upload the project to Smithed using the credentials and the configuration

	Args:
		credentials		(dict[str, str]):	Credentials for the Smithed API
		smithed_config	(dict):				Configuration for the Smithed project
		changelog		(str):				Changelog text for the release
	"""
	api_key, author = validate_credentials(credentials)
	project_id, project_name, version = validate_config(smithed_config)

	upload_version(project_id, project_name, version, api_key, author)

	stp.info(f"Project {project_name} updated on Smithed!")


