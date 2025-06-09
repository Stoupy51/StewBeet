
# Imports
import json
import os

import requests
import stouputils as stp

from .cd_utils import get_supported_versions, handle_response

# Constants
MODRINTH_API_URL: str = "https://api.modrinth.com/v2"
PROJECT_ENDPOINT: str = f"{MODRINTH_API_URL}/project"
VERSION_ENDPOINT: str = f"{MODRINTH_API_URL}/version"

def validate_credentials(credentials: dict[str, str]) -> str:
	""" Get and validate Modrinth credentials

	Args:
		credentials (dict[str, str]): Credentials for the Modrinth API
	Returns:
		str: API key for Modrinth
	"""
	if "modrinth_api_key" not in credentials:
		raise ValueError("The credentials file must contain a 'modrinth_api_key' key, which is a PAT (Personal Access Token) for the Modrinth API: https://modrinth.com/settings/pats")
	return credentials["modrinth_api_key"]

def validate_config(modrinth_config: dict[str, str]) -> tuple[str, str, str, str, str, str, str]:
	""" Validate Modrinth configuration

	Args:
		modrinth_config (dict[str, str]): Configuration for the Modrinth project
	Returns:
		str: Project name on Modrinth
		str: Version of the project
		str: Slug (namespace) of the project
		str: Summary of the project
		str: Description in Markdown format
		str: Version type (release, beta, alpha)
		str: Build folder path
	"""
	required_keys = [
		"project_name", "version", "slug", "summary",
		"description_markdown", "version_type", "build_folder"
	]
	error_messages = {
		"project_name": "name of the project on Modrinth",
		"version": "version of the project",
		"slug": "namespace of the project",
		"summary": "summary of the project",
		"description_markdown": "description of the project in Markdown format",
		"version_type": "version type of the project (release, beta, alpha)",
		"build_folder": "folder containing the build of the project (datapack and resourcepack zip files)"
	}

	for key in required_keys:
		if key not in modrinth_config:
			raise ValueError(f"The modrinth_config dictionary must contain a '{key}' key, which is the {error_messages[key]}")

	return (
		modrinth_config["project_name"],
		modrinth_config["version"],
		modrinth_config["slug"],
		modrinth_config["summary"],
		modrinth_config["description_markdown"],
		modrinth_config["version_type"],
		modrinth_config["build_folder"]
	)

def get_project(slug: str, headers: dict[str, str]) -> dict:
	""" Get project from Modrinth

	Args:
		slug (str): Project slug/namespace
		headers (dict[str, str]): Headers for Modrinth API requests
	Returns:
		dict: Project data
	"""
	stp.progress(f"Getting project {slug} from Modrinth")
	search_response = requests.get(f"{PROJECT_ENDPOINT}/{slug}", headers=headers)
	handle_response(search_response, f"Project not found on Modrinth, with namespace {slug}, please create it manually on https://modrinth.com/")
	return search_response.json()

def update_project_description(slug: str, description: str, summary: str, headers: dict[str, str]) -> None:
	""" Update project description and summary

	Args:
		slug (str): Project slug/namespace
		description (str): Project description in Markdown
		summary (str): Project summary
		headers (dict[str, str]): Headers for Modrinth API requests
	"""
	stp.progress("Updating project description")
	update_response = requests.patch(
		f"{PROJECT_ENDPOINT}/{slug}",
		headers=headers,
		json={"body": description.strip(), "description": summary.strip()}
	)
	handle_response(update_response, "Failed to update project description")

def handle_existing_version(slug: str, version: str, headers: dict[str, str]) -> bool:
	""" Check and handle existing version

	Args:
		slug (str): Project slug/namespace
		version (str): Version to check
		headers (dict[str, str]): Headers for Modrinth API requests
	Returns:
		bool: True if we should continue, False otherwise
	"""
	version_response = requests.get(f"{PROJECT_ENDPOINT}/{slug}/version/{version}", headers=headers)
	if version_response.status_code == 200:
		stp.warning(f"Version {version} already exists on Modrinth, do you want to delete it? (y/N)")
		if input().lower() != "y":
			return False
		version_id: str = version_response.json()["id"]
		delete_response = requests.delete(f"{VERSION_ENDPOINT}/{version_id}", headers=headers)
		handle_response(delete_response, "Failed to delete the version")
	elif version_response.status_code == 404:
		stp.info(f"Version {version} not found on Modrinth, uploading...")
	else:
		stp.handle_response(version_response, "Failed to check if the version already exists")
	return True

def get_file_parts(project_name: str, build_folder: str) -> list[str]:
	""" Get file parts to upload

	Args:
		project_name (str): Name of the project
		build_folder (str): Path to build folder
	Returns:
		list[str]: List of file paths to upload
	"""
	file_parts: list[str] = [
		f"{build_folder}/{project_name}_datapack_with_libs.zip",
		f"{build_folder}/{project_name}_resource_pack_with_libs.zip"
	]
	file_parts = [file_part for file_part in file_parts if os.path.exists(file_part)]
	if len(file_parts) == 0:
		file_parts = [
			f"{build_folder}/{project_name}_datapack.zip",
			f"{build_folder}/{project_name}_resource_pack.zip"
		]
		file_parts = [file_part for file_part in file_parts if os.path.exists(file_part)]
	if len(file_parts) == 0:
		raise ValueError(f"No file parts (datapack and resourcepack zip files) found in {build_folder}, please check the build_folder path in the modrinth_config file")
	return file_parts

def upload_version(
	project_id: str,
	project_name: str,
	version: str,
	version_type: str,
	changelog: str,
	file_parts: list[str],
	headers: dict[str, str],
	dependencies: list[str] | None = None
) -> dict:
	""" Upload new version

	Args:
		project_id		(str):				Modrinth project ID
		project_name	(str):				Name of the project
		version			(str):				Version number
		version_type	(str):				Type of version (release, beta, alpha)
		changelog		(str):				Changelog text
		file_parts		(list[str]):		List of files to upload
		headers			(dict[str, str]):	Headers for Modrinth API requests
		dependencies	(list[str]):		List of dependencies
	Returns:
		dict: Upload response data
	"""
	if dependencies is None:
		dependencies = []
	stp.progress(f"Creating version {version}")
	files: dict[str, bytes] = {}
	for file_part in file_parts:
		stp.progress(f"Reading file {os.path.basename(file_part)}")
		with open(file_part, "rb") as file:
			files[os.path.basename(file_part)] = file.read()

	request_data: dict = {
		"name": f"{project_name} [v{version}]",
		"version_number": version,
		"changelog": changelog,
		"dependencies": dependencies,
		"game_versions": get_supported_versions(),
		"version_type": version_type,
		"loaders": ["datapack"],
		"featured": False,
		"status": "listed",
		"project_id": project_id,
		"file_parts": [os.path.basename(file_part) for file_part in file_parts],
		"primary_file": os.path.basename(file_parts[0])
	}

	upload_response = requests.post(
		VERSION_ENDPOINT,
		headers=headers,
		data={"data": json.dumps(request_data)},
		files=files,
		timeout=10,
		stream=False
	)
	json_response: dict = upload_response.json()
	handle_response(upload_response, "Failed to upload the version")
	return json_response

def set_resource_pack_required(version_id: str, resource_pack_hash: str, headers: dict[str, str]) -> None:
	""" Set resource pack as required

	Args:
		version_id (str): ID of the version
		resource_pack_hash (str): SHA1 hash of resource pack
		headers (dict[str, str]): Headers for Modrinth API requests
	"""
	stp.progress("Setting resource pack as required")
	version_response = requests.patch(
		f"{VERSION_ENDPOINT}/{version_id}",
		headers=headers,
		json={"file_types": [{"algorithm": "sha1", "hash": resource_pack_hash, "file_type": "required-resource-pack"}]}
	)
	handle_response(version_response, "Failed to put the resource pack as required")

@stp.measure_time(stp.progress, "Uploading to modrinth took")
@stp.handle_error()
def upload_to_modrinth(credentials: dict[str, str], modrinth_config: dict, changelog: str = "") -> None:
	""" Upload the project to Modrinth using the credentials and the configuration

	Args:
		credentials		(dict[str, str]):	Credentials for the Modrinth API
		modrinth_config	(dict):				Configuration for the Modrinth project
		changelog		(str):				Changelog text for the release
	"""
	api_key = validate_credentials(credentials)
	headers: dict[str, str] = {"Authorization": api_key}

	project_name, version, slug, summary, description_markdown, version_type, build_folder = validate_config(modrinth_config)

	project = get_project(slug, headers)
	update_project_description(slug, description_markdown, summary, headers)
	can_continue: bool = handle_existing_version(slug, version, headers)
	if not can_continue:
		return

	file_parts = get_file_parts(project_name, build_folder)

	json_response = upload_version(
		project["id"], project_name, version, version_type,
		changelog, file_parts, headers, modrinth_config.get("dependencies", [])
	)

	if len(file_parts) > 1:
		resource_pack_hash: str = json_response["files"][1]["hashes"]["sha1"]
		set_resource_pack_required(json_response["id"], resource_pack_hash, headers)

	stp.info(f"Project {project_name} updated on Modrinth!")


