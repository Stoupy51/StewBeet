
# Imports
import json
import os
import zipfile

import requests
import stouputils as stp
from beet.core.utils import JsonDict

from .cd_utils import get_supported_versions

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

def validate_config(modrinth_config: JsonDict) -> tuple[str, str, str, str, str, str, str]:
	""" Validate Modrinth configuration

	Args:
		modrinth_config (JsonDict): Configuration for the Modrinth project
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
	if isinstance(modrinth_config.get("authors"), str):
		modrinth_config["authors"] = [x.strip() for x in modrinth_config["authors"].split(",")]

	return (
		modrinth_config["project_name"],
		modrinth_config["version"],
		modrinth_config["slug"],
		modrinth_config["summary"],
		modrinth_config["description_markdown"],
		modrinth_config["version_type"],
		modrinth_config["build_folder"]
	)

def get_project(slug: str, headers: dict[str, str]) -> dict[str, str]:
	""" Get project from Modrinth

	Args:
		slug (str): Project slug/namespace
		headers (dict[str, str]): Headers for Modrinth API requests
	Returns:
		dict: Project data
	"""
	stp.progress(f"Getting project {slug} from Modrinth")
	search_response = requests.get(f"{PROJECT_ENDPOINT}/{slug}", headers=headers)
	stp.handle_response(search_response, f"Project not found on Modrinth, with namespace {slug}, please create it manually on https://modrinth.com/")
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
	stp.handle_response(update_response, "Failed to update project description")

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
		stp.handle_response(delete_response, "Failed to delete the version")
	elif version_response.status_code == 404:
		stp.info(f"Version {version} not found on Modrinth, uploading...")
	else:
		stp.handle_response(version_response, "Failed to check if the version already exists")
	return True

def generate_fabric_metadata(mod_id: str, metadata: JsonDict) -> str:
	""" Generate Fabric mod metadata JSON

	Args:
		mod_id (str): Mod ID
		metadata (dict): Mod metadata
	Returns:
		str: Fabric mod.json content
	"""
	fabric_mod_json: JsonDict = {
		"schemaVersion": 1,
		"id": f"stewbeet_{mod_id}",
		"version": metadata["version"],
		"name": metadata["name"],
		"description": metadata.get("description", ""),
		"authors": metadata.get("authors", []),
		"contact": {"homepage": f"https://modrinth.com/datapack/{mod_id}"},
		"license": metadata.get("license", "All Rights Reserved"),
		"icon": f"{mod_id}_pack.png",
		"environment": "*",
		"depends": {"fabric-resource-loader-v0": "*"}
	}

	# Add optional contact fields
	if metadata.get("sources"):
		fabric_mod_json["contact"]["sources"] = metadata["sources"]
	if metadata.get("issues"):
		fabric_mod_json["contact"]["issues"] = metadata["issues"]
	return stp.json_dump(fabric_mod_json, max_level=-1)

def generate_forge_metadata(mod_id: str, metadata: JsonDict, is_neoforge: bool = False) -> str:
	""" Generate Forge/NeoForge mod metadata TOML

	Args:
		mod_id (str): Mod ID
		metadata (dict): Mod metadata
		is_neoforge (bool): Whether this is for NeoForge (uses javafml) or Forge (uses lowcodefml)
	Returns:
		str: mods.toml content
	"""
	description: str = metadata.get("description", "").replace(chr(10), "\\n").replace('"', '\\"')
	authors: str = ", ".join(metadata.get("authors", []))
	homepage: str = f"https://modrinth.com/datapack/{mod_id}"
	mod_loader: str = "'javafml'" if is_neoforge else "'lowcodefml'"
	loader_version: str = "'[1,)'" if is_neoforge else "'[40,)'"

	toml_content: str = f"""
modLoader = {mod_loader}
loaderVersion = {loader_version}
license = '{metadata.get("license", "All Rights Reserved")}'
showAsResourcePack = false
mods = [
	{{ modId = 'stewbeet_{mod_id}', version = '{metadata["version"]}', displayName = '{metadata["name"]}', description = "{description}", logoFile = '{mod_id}_pack.png'"""

	# Add optional fields
	if homepage:
		update_url = f"https://api.modrinth.com/updates/{mod_id}/forge_updates.json"
		if is_neoforge:
			update_url += "?neoforge=only"
		toml_content += f""", updateJSONURL = '{update_url}'"""
	toml_content += f""", credits = 'Generated by StewBeet', authors = '{authors}', displayURL = '{homepage}' }},
]
"""
	# Add issue tracker if available
	if metadata.get("issues"):
		toml_content += f"issueTrackerURL = '{metadata['issues']}'\n"
	return toml_content

def generate_quilt_metadata(mod_id: str, metadata: JsonDict) -> str:
	""" Generate Quilt mod metadata JSON

	Args:
		mod_id (str): Mod ID
		metadata (dict): Mod metadata
	Returns:
		str: quilt.mod.json content
	"""
	# Build contributors dictionary
	contributors: JsonDict = {}
	for author in metadata.get("authors", []):
		contributors[author] = "Member"

	# Build contact dictionary
	contact: JsonDict = {"homepage": f"https://modrinth.com/datapack/{mod_id}"}
	if metadata.get("sources"):
		contact["sources"] = metadata["sources"]
	if metadata.get("issues"):
		contact["issues"] = metadata["issues"]

	quilt_mod_json: JsonDict = {
		"schema_version": 1,
		"quilt_loader": {
			"group": "com.stewbeet",
			"id": f"stewbeet_{mod_id}",
			"version": metadata["version"],
			"metadata": {
				"name": metadata["name"],
				"description": metadata.get("description", ""),
				"contributors": contributors,
				"contact": contact,
				"icon": f"{mod_id}_pack.png"
			},
			"intermediate_mappings": "net.fabricmc:intermediary",
			"depends": [
				{
					"id": "quilt_resource_loader",
					"versions": "*",
					"unless": "fabric-resource-loader-v0"
				}
			]
		}
	}
	return stp.json_dump(quilt_mod_json, max_level=-1)

def convert_datapack_to_mod(
	datapack_path: str,
	output_path: str,
	metadata: JsonDict,
	platforms: list[str],
	resource_pack_path: str | None = None
) -> None:
	""" Convert a datapack ZIP to a mod JAR with proper metadata files

	Args:
		datapack_path (str): Path to the datapack ZIP file
		output_path (str): Path where to save the mod JAR file
		metadata (dict): Mod metadata (id, name, version, description, authors, etc.)
		platforms (list[str]): List of platforms (fabric, forge, neoforge, quilt)
		resource_pack_path (str): Optional path to the resource pack ZIP file
	"""
	# Create a new ZIP/JAR file with datapack + resource pack content + mod metadata
	with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as mod_zip:

		# Determine mod ID
		mod_id = metadata.get("id", metadata.get("slug", metadata["name"])).lower().replace(" ", "_").replace("-", "_")

		# Copy all files from datapack
		with zipfile.ZipFile(datapack_path, 'r') as datapack_zip:
			for item in datapack_zip.infolist():
				data = datapack_zip.read(item.filename)
				mod_zip.writestr(item, data)
				if item.filename == "pack.png":
					mod_zip.writestr(f"{mod_id}_pack.png", data)

		# Copy assets folder from resource pack if provided
		if resource_pack_path and os.path.exists(resource_pack_path):
			with zipfile.ZipFile(resource_pack_path, 'r') as resource_pack_zip:
				for item in resource_pack_zip.infolist():
					# Only copy files from the assets folder (exclude pack.png and pack.mcmeta)
					if item.filename.startswith("assets/") and not item.is_dir():
						data = resource_pack_zip.read(item.filename)
						mod_zip.writestr(item, data)

		# Generate platform-specific metadata files
		if "fabric" in platforms:
			mod_zip.writestr("fabric.mod.json", generate_fabric_metadata(mod_id, metadata))

		if "forge" in platforms:
			mod_zip.writestr("META-INF/mods.toml", generate_forge_metadata(mod_id, metadata, is_neoforge=False))

		if "neoforge" in platforms:
			mod_zip.writestr("META-INF/neoforge.mods.toml", generate_forge_metadata(mod_id, metadata, is_neoforge=True))

		if "quilt" in platforms:
			mod_zip.writestr("quilt.mod.json", generate_quilt_metadata(mod_id, metadata))

def get_file_parts(project_name: str, build_folder: str, modrinth_config: JsonDict, project_data: JsonDict | None = None) -> list[str]:
	""" Get file parts to upload

	Args:
		project_name (str): Name of the project
		build_folder (str): Path to build folder
		modrinth_config (dict): Modrinth configuration
		project_data (dict): Optional project data from Modrinth API
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

	# Convert datapack to mod if requested
	package_as_mod: str | None = modrinth_config.get("package_as_mod", None)
	if package_as_mod in ["all", "separate"]:

		# Find the datapack file and resourcepack file
		datapack_file: str = ""
		resource_pack_file: str = ""
		for file_part in file_parts:
			if "datapack" in file_part.lower():
				datapack_file = file_part
			elif "resource_pack" in file_part.lower():
				resource_pack_file = file_part

		if datapack_file:

			# Get mod platforms (default to all platforms)
			platforms = modrinth_config.get("mod_platforms", ["fabric", "forge", "neoforge", "quilt"])
			if isinstance(platforms, str):
				platforms = [platforms]

			# Prepare base metadata
			base_metadata: JsonDict = {
				"id": modrinth_config.get("slug", project_name).lower().replace("-", "_").replace(" ", "_"),
				"name": project_name,
				"version": modrinth_config.get("version", "1.0.0"),
				"description": modrinth_config.get("summary", ""),
				"authors": modrinth_config.get("authors", []),
				"license": modrinth_config.get("license", "All Rights Reserved"),
				"homepage": modrinth_config.get("homepage"),
				"sources": modrinth_config.get("sources"),
				"issues": modrinth_config.get("issues"),
				"icon": modrinth_config.get("icon")
			}

			# Complete metadata from Modrinth project if available
			if project_data:
				# Use existing project data to fill missing metadata
				if not base_metadata.get("description") and project_data.get("description"):
					base_metadata["description"] = project_data["description"]
				if not base_metadata.get("license") or base_metadata["license"] == "All Rights Reserved":
					if project_data.get("license") and project_data["license"].get("id"):
						base_metadata["license"] = project_data["license"]["id"]
				if not base_metadata.get("homepage") and project_data.get("project_url"):
					base_metadata["homepage"] = project_data["project_url"]
				if not base_metadata.get("sources") and project_data.get("source_url"):
					base_metadata["sources"] = project_data["source_url"]
				if not base_metadata.get("issues") and project_data.get("issues_url"):
					base_metadata["issues"] = project_data["issues_url"]
				if project_data.get("title"):
					base_metadata["name"] = project_data["title"]

			# Create one mod with all platforms
			if package_as_mod == "all":
				mod_output_path: str = f"{build_folder}/{project_name}_mod.jar"
				with stp.MeasureTime(stp.progress, message=f"Converted datapack to mod for platforms: {', '.join(platforms)}"):
					convert_datapack_to_mod(datapack_file, mod_output_path, base_metadata, platforms, resource_pack_file)

				# Add mod file to file_parts (keep datapack too)
				file_parts.append(mod_output_path)

			# Create separate mod for each platform
			elif package_as_mod == "separate":
				for platform in platforms:
					platform_metadata = base_metadata.copy()
					platform_metadata["name"] = project_name
					mod_output_path = f"{build_folder}/{project_name}_{platform}_mod.jar"
					with stp.MeasureTime(stp.progress, message=f"Converted datapack to mod for platform: {platform}"):
						convert_datapack_to_mod(datapack_file, mod_output_path, platform_metadata, [platform], resource_pack_file)

					# Add platform-specific mod to file_parts
					file_parts.append(mod_output_path)

	return file_parts

def upload_version(
	project_id: str,
	project_name: str,
	version: str,
	version_type: str,
	changelog: str,
	file_parts: list[str],
	headers: dict[str, str],
	dependencies: list[str] | None = None,
	loaders: list[str] | None = None
) -> JsonDict:
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
		loaders			(list[str]):		List of loaders (datapack, fabric, forge, etc.)
	Returns:
		dict: Upload response data
	"""
	if dependencies is None:
		dependencies = []
	if loaders is None:
		loaders = ["datapack"]
	stp.progress(f"Creating version {version}")
	files: dict[str, bytes] = {}
	for file_part in file_parts:
		stp.progress(f"Reading file {os.path.basename(file_part)}")
		with open(file_part, "rb") as file:
			files[os.path.basename(file_part)] = file.read()

	request_data: JsonDict = {
		"name": f"{project_name} [v{version}]",
		"version_number": version,
		"changelog": changelog,
		"dependencies": dependencies,
		"game_versions": get_supported_versions(),
		"version_type": version_type,
		"loaders": loaders,
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
	json_response: JsonDict = upload_response.json()
	stp.handle_response(upload_response, "Failed to upload the version")
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
	stp.handle_response(version_response, "Failed to put the resource pack as required")

@stp.measure_time(stp.progress, "Uploading to modrinth took")
@stp.handle_error()
def upload_to_modrinth(credentials: dict[str, str], modrinth_config: JsonDict, changelog: str = "") -> None:
	""" Upload the project to Modrinth using the credentials and the configuration

	Args:
		credentials		(dict[str, str]):	Credentials for the Modrinth API
		modrinth_config	(dict):				Configuration for the Modrinth project
		changelog		(str):				Changelog text for the release
	"""
	api_key: str = validate_credentials(credentials)
	headers: dict[str, str] = {"Authorization": api_key}

	project_name, version, slug, summary, description_markdown, version_type, build_folder = validate_config(modrinth_config)

	project = get_project(slug, headers)
	update_project_description(slug, description_markdown, summary, headers)
	can_continue: bool = handle_existing_version(slug, version, headers)
	if not can_continue:
		return

	file_parts = get_file_parts(project_name, build_folder, modrinth_config, project)

	package_as_mod = modrinth_config.get("package_as_mod", None)
	mod_platforms = modrinth_config.get("mod_platforms", ["fabric", "forge", "neoforge", "quilt"])
	if isinstance(mod_platforms, str):
		mod_platforms = [mod_platforms]

	# Handle different packaging modes
	if package_as_mod == "all":
		# Upload datapack version first
		datapack_files = [f for f in file_parts if "_datapack" in f or "_resource_pack" in f]
		if datapack_files:
			stp.info("Uploading datapack version...")
			json_response = upload_version(
				project["id"], project_name, version, version_type,
				changelog, datapack_files, headers, modrinth_config.get("dependencies", []),
				["datapack"]
			)
			if len(datapack_files) > 1:
				resource_pack_hash: str = json_response["files"][1]["hashes"]["sha1"]
				set_resource_pack_required(json_response["id"], resource_pack_hash, headers)

		# Upload mod version (with all platforms)
		mod_files = [f for f in file_parts if "_mod" in f and "_datapack" not in f]
		if mod_files:
			# Check if mod version already exists
			mod_version_name = f"{version}+mod"
			can_continue_mod = handle_existing_version(slug, mod_version_name, headers)
			if can_continue_mod:
				stp.info(f"Uploading mod version (all platforms: {', '.join(mod_platforms)})...")
				upload_version(
					project["id"], project_name, mod_version_name, version_type,
					changelog, mod_files, headers, modrinth_config.get("dependencies", []),
					mod_platforms
				)

	elif package_as_mod == "separate":
		# Upload datapack version first
		datapack_files = [f for f in file_parts if "_datapack" in f or "_resource_pack" in f]
		if datapack_files:
			stp.info("Uploading datapack version...")
			json_response = upload_version(
				project["id"], project_name, version, version_type,
				changelog, datapack_files, headers, modrinth_config.get("dependencies", []),
				["datapack"]
			)
			if len(datapack_files) > 1:
				resource_pack_hash: str = json_response["files"][1]["hashes"]["sha1"]
				set_resource_pack_required(json_response["id"], resource_pack_hash, headers)

		# Upload separate version for each platform
		for platform in mod_platforms:
			platform_files = [f for f in file_parts if f"_{platform}" in f]
			if platform_files:
				platform_version_name = f"{version}+{platform}"
				can_continue_platform = handle_existing_version(slug, platform_version_name, headers)
				if can_continue_platform:
					stp.info(f"Uploading {platform} version...")
					upload_version(
						project["id"], project_name, platform_version_name, version_type,
						changelog, platform_files, headers, modrinth_config.get("dependencies", []),
						[platform]
					)

	else:
		# Default: upload as datapack only
		json_response = upload_version(
			project["id"], project_name, version, version_type,
			changelog, file_parts, headers, modrinth_config.get("dependencies", []),
			["datapack"]
		)
		if len(file_parts) > 1:
			resource_pack_hash: str = json_response["files"][1]["hashes"]["sha1"]
			set_resource_pack_required(json_response["id"], resource_pack_hash, headers)

	stp.info(f"Project {project_name} updated on Modrinth!")


