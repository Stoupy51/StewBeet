
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import json
import os
import zipfile
from dataclasses import dataclass

import requests
import stouputils as stp
from stouputils.typing import JsonDict

from .cd_utils import get_supported_versions

# Constants
MODRINTH_API_URL: str = "https://api.modrinth.com/v2"
PROJECT_ENDPOINT: str = f"{MODRINTH_API_URL}/project"
VERSION_ENDPOINT: str = f"{MODRINTH_API_URL}/version"
MOD_PLATFORMS: list[str] = ["fabric", "forge", "neoforge", "quilt"]
""" Every platform a datapack is packaged as a mod for, unless `mod_platforms` names some. """
PROJECT_FALLBACKS: tuple[tuple[str, str], ...] = (
	("description", "description"), ("homepage", "project_url"), ("sources", "source_url"), ("issues", "issues_url"),
)
""" Mod metadata a Modrinth project field fills when the config leaves it empty. """

def validate_credentials(credentials: dict[str, str]) -> str:
	""" Get and validate Modrinth credentials

	Args:
		credentials: Credentials for the Modrinth API
	Returns:
		str: API key for Modrinth
	"""
	if "modrinth_api_key" not in credentials:
		raise ValueError(
			"The credentials file must contain a 'modrinth_api_key' key, "
			"which is a PAT (Personal Access Token) for the Modrinth API: https://modrinth.com/settings/pats"
		)
	return credentials["modrinth_api_key"]

def validate_config(modrinth_config: JsonDict) -> tuple[str, str, str, str, str, str, str]:
	""" Validate Modrinth configuration

	Args:
		modrinth_config: Configuration for the Modrinth project
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
		modrinth_config["project_name"].replace(" ", ""),
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
		slug:    Project slug/namespace
		headers: Headers for Modrinth API requests
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
		slug:        Project slug/namespace
		description: Project description in Markdown
		summary:     Project summary
		headers:     Headers for Modrinth API requests
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
		slug:    Project slug/namespace
		version: Version to check
		headers: Headers for Modrinth API requests
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
		mod_id:   Mod ID
		metadata: Mod metadata
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
		mod_id:      Mod ID
		metadata:    Mod metadata
		is_neoforge: Whether this is for NeoForge (uses javafml) or Forge (uses lowcodefml)
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
	{{ modId = 'stewbeet_{mod_id}', version = '{metadata["version"]}', displayName = '{metadata["name"]}', description = "{description}", logoFile = '{mod_id}_pack.png'"""  # noqa: E501

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
		mod_id:   Mod ID
		metadata: Mod metadata
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
		datapack_path:      Path to the datapack ZIP file
		output_path:        Path where to save the mod JAR file
		metadata:           Mod metadata (id, name, version, description, authors, etc.)
		platforms:          List of platforms (fabric, forge, neoforge, quilt)
		resource_pack_path: Optional path to the resource pack ZIP file
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
		project_name:    Name of the project
		build_folder:    Path to build folder
		modrinth_config: Modrinth configuration
		project_data:    Optional project data from Modrinth API
	Returns:
		list[str]: List of file paths to upload
	"""
	file_parts: list[str] = existing_packs(project_name, build_folder)
	package_as_mod: str | None = modrinth_config.get("package_as_mod", None)
	datapack_file: str = next((part for part in reversed(file_parts) if "datapack" in part.lower()), "")
	if package_as_mod not in ["all", "separate"] or not datapack_file:
		return file_parts
	resource_pack_file: str = next(
		(part for part in reversed(file_parts) if "resource_pack" in part.lower() and "datapack" not in part.lower()), ""
	)

	platforms: list[str] = mod_platforms(modrinth_config)
	base_metadata: JsonDict = mod_metadata(project_name, modrinth_config, project_data)
	if package_as_mod == "all":
		mod_output_path: str = f"{build_folder}/{project_name}_mod.jar"
		with stp.MeasureTime(stp.progress, message=f"Converted datapack to mod for platforms: {', '.join(platforms)}"):
			convert_datapack_to_mod(datapack_file, mod_output_path, base_metadata, platforms, resource_pack_file)
		file_parts.append(mod_output_path)
		return file_parts

	# A separate mod per platform
	for platform in platforms:
		mod_output_path = f"{build_folder}/{project_name}_{platform}_mod.jar"
		with stp.MeasureTime(stp.progress, message=f"Converted datapack to mod for platform: {platform}"):
			platform_metadata: JsonDict = {**base_metadata, "name": project_name}
			convert_datapack_to_mod(datapack_file, mod_output_path, platform_metadata, [platform], resource_pack_file)
		file_parts.append(mod_output_path)
	return file_parts

def existing_packs(project_name: str, build_folder: str) -> list[str]:
	""" The datapack and resource pack zips of the build, bundled with their libraries when it made those.

	Raises:
		ValueError: When the build folder holds neither.
	"""
	for suffix in ("_with_libs", ""):
		packs: tuple[str, str] = (f"{project_name}_datapack{suffix}.zip", f"{project_name}_resource_pack{suffix}.zip")
		file_parts: list[str] = [f"{build_folder}/{pack}" for pack in packs if os.path.exists(f"{build_folder}/{pack}")]
		if file_parts:
			return file_parts
	raise ValueError(
		f"No file parts (datapack and resourcepack zip files) found in {build_folder}, "
		"please check the build_folder path in the modrinth_config file"
	)

def mod_platforms(modrinth_config: JsonDict) -> list[str]:
	""" The platforms to package the mod for, `mod_platforms` being one name or a list of them. """
	platforms: str | list[str] = modrinth_config.get("mod_platforms", MOD_PLATFORMS)
	return [platforms] if isinstance(platforms, str) else platforms

def mod_metadata(project_name: str, modrinth_config: JsonDict, project_data: JsonDict | None) -> JsonDict:
	""" The mod's metadata from the config, completed by the Modrinth project, whose title also names the mod. """
	metadata: JsonDict = {
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
	if not project_data:
		return metadata
	for key, field in PROJECT_FALLBACKS:
		if not metadata.get(key) and project_data.get(field):
			metadata[key] = project_data[field]
	license_is_placeholder: bool = not metadata.get("license") or metadata["license"] == "All Rights Reserved"
	if license_is_placeholder and project_data.get("license") and project_data["license"].get("id"):
		metadata["license"] = project_data["license"]["id"]
	if project_data.get("title"):
		metadata["name"] = project_data["title"]
	return metadata


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
		project_id:   Modrinth project ID
		project_name: Name of the project
		version:      Version number
		version_type: Type of version (release, beta, alpha)
		changelog:    Changelog text
		file_parts:   List of files to upload
		headers:      Headers for Modrinth API requests
		dependencies: List of dependencies
		loaders:      List of loaders (datapack, fabric, forge, etc.)
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
		version_id:         ID of the version
		resource_pack_hash: SHA1 hash of resource pack
		headers:            Headers for Modrinth API requests
	"""
	stp.progress("Setting resource pack as required")
	version_response = requests.patch(
		f"{VERSION_ENDPOINT}/{version_id}",
		headers=headers,
		json={"file_types": [{"algorithm": "sha1", "hash": resource_pack_hash, "file_type": "required-resource-pack"}]}
	)
	stp.handle_response(version_response, "Failed to put the resource pack as required")

@stp.measure_time(message="Uploading to modrinth took")
@stp.handle_error
def upload_to_modrinth(credentials: dict[str, str], modrinth_config: JsonDict, changelog: str = "") -> None:
	""" Upload the project to Modrinth using the credentials and the configuration

	Args:
		credentials:     Credentials for the Modrinth API
		modrinth_config: Configuration for the Modrinth project
		changelog:       Changelog text for the release
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
	release: Release = Release(
		project_id=project["id"],
		project_name=project_name,
		version_type=version_type,
		changelog=changelog,
		headers=headers,
		dependencies=modrinth_config.get("dependencies", []),
	)
	package_as_mod = modrinth_config.get("package_as_mod", None)
	if package_as_mod in ("all", "separate"):
		pack_files: list[str] = [f for f in file_parts if "_datapack" in f or "_resource_pack" in f]
		if pack_files:
			stp.info("Uploading datapack version...")
			release.upload_pack(version, pack_files)
		platforms: list[str] = mod_platforms(modrinth_config)
		upload_mods(release, slug, version, file_parts, every_platform=package_as_mod == "all", platforms=platforms)
	else:
		release.upload_pack(version, file_parts)
	stp.info(f"Project {project_name} updated on Modrinth!")

def upload_mods(release: Release, slug: str, version: str, file_parts: list[str], every_platform: bool, platforms: list[str]) -> None:
	""" Upload the mod as one version for all platforms (`<version>+mod`), or one per platform (`<version>+<platform>`). """
	if every_platform:
		mod_files: list[str] = [f for f in file_parts if "_mod" in f and "_datapack" not in f]
		if mod_files and handle_existing_version(slug, f"{version}+mod", release.headers):
			stp.info(f"Uploading mod version (all platforms: {', '.join(platforms)})...")
			release.upload(f"{version}+mod", mod_files, platforms)
		return
	for platform in platforms:
		platform_files: list[str] = [f for f in file_parts if f"_{platform}" in f]
		if platform_files and handle_existing_version(slug, f"{version}+{platform}", release.headers):
			stp.info(f"Uploading {platform} version...")
			release.upload(f"{version}+{platform}", platform_files, [platform])

@dataclass(frozen=True)
class Release:
	""" What every version uploaded for one release of a project shares. """
	project_id: str
	project_name: str
	version_type: str
	changelog: str
	headers: dict[str, str]
	dependencies: list[str]

	def upload(self, version: str, files: list[str], loaders: list[str]) -> JsonDict:
		""" Upload one version of the release. """
		return upload_version(
			self.project_id, self.project_name, version, self.version_type, self.changelog,
			files, self.headers, self.dependencies, loaders,
		)

	def upload_pack(self, version: str, files: list[str]) -> None:
		""" Upload the datapack version, its second file being the resource pack it requires. """
		json_response: JsonDict = self.upload(version, files, ["datapack"])
		if len(files) > 1:
			set_resource_pack_required(json_response["id"], json_response["files"][1]["hashes"]["sha1"], self.headers)

