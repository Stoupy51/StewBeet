
# Imports
import os

import requests
import stouputils as stp

from .cd_utils import handle_response

# Constants
GITHUB_API_URL: str = "https://api.github.com"
PROJECT_ENDPOINT: str = f"{GITHUB_API_URL}/repos"
COMMIT_TYPES: dict[str, str] = {
	"feat":		"Features",
	"fix":		"Bug Fixes",
	"docs":		"Documentation",
	"style":	"Style",
	"refactor":	"Code Refactoring",
	"perf":		"Performance Improvements",
	"test":		"Tests",
	"build":	"Build System",
	"ci":		"CI/CD",
	"chore":	"Chores",
	"revert":	"Reverts",
	"uwu":		"UwU ༼ つ ◕_◕ ༽つ",
}

def validate_credentials(credentials: dict[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
	""" Get and validate GitHub credentials

	Args:
		credentials (dict[str, dict[str, str]]):	Credentials for the GitHub API
	Returns:
		str:			Owner (the username of the account to use)
		dict[str, str]:	Headers (for the requests to the GitHub API)
	"""
	if "github" not in credentials:
		raise ValueError("The credentials file must contain a 'github' key, which is a dictionary containing a 'api_key' key (a PAT for the GitHub API: https://github.com/settings/tokens) and a 'username' key (the username of the account to use)")
	if "api_key" not in credentials["github"]:
		raise ValueError("The credentials file must contain a 'github' key, which is a dictionary containing a 'api_key' key (a PAT for the GitHub API: https://github.com/settings/tokens) and a 'username' key (the username of the account to use)")
	if "username" not in credentials["github"]:
		raise ValueError("The credentials file must contain a 'github' key, which is a dictionary containing a 'api_key' key (a PAT for the GitHub API: https://github.com/settings/tokens) and a 'username' key (the username of the account to use)")
	
	api_key: str = credentials["github"]["api_key"]
	owner: str = credentials["github"]["username"]
	headers: dict[str, str] = {"Authorization": f"Bearer {api_key}"}
	return owner, headers

def validate_config(github_config: dict[str, str]) -> tuple[str, str, str]:
	""" Validate GitHub configuration

	Args:
		github_config (dict[str, str]):	Configuration for the GitHub project
	Returns:
		str: Project name on GitHub
		str: Version of the project
		str: Build folder path containing zip files
	"""
	if "project_name" not in github_config:
		raise ValueError("The github_config file must contain a 'project_name' key, which is the name of the project on GitHub")
	if "version" not in github_config:
		raise ValueError("The github_config file must contain a 'version' key, which is the version of the project")
	if "build_folder" not in github_config:
		raise ValueError("The github_config file must contain a 'build_folder' key, which is the folder containing the build of the project (datapack and resourcepack zip files)")
	
	return github_config["project_name"], github_config["version"], github_config["build_folder"]

def handle_existing_tag(owner: str, project_name: str, version: str, headers: dict[str, str]) -> bool:
	""" Check if tag exists and handle deletion if needed

	Args:
		owner (str):				GitHub username
		project_name (str):			Name of the GitHub repository
		version (str):				Version to check for existing tag
		headers (dict[str, str]):	Headers for GitHub API requests
	Returns:
		bool: True if the tag was deleted or if it was not found, False otherwise
	"""
	tag_url = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/git/refs/tags/v{version}"
	response = requests.get(tag_url, headers=headers)
	if response.status_code == 200:
		stp.warning(f"A tag v{version} already exists. Do you want to delete it? (y/N): ")
		if input().lower() == "y":
			delete_existing_release(owner, project_name, version, headers)
			delete_existing_tag(tag_url, headers)
			return True
		else:
			return False
	return True

def delete_existing_release(owner: str, project_name: str, version: str, headers: dict[str, str]) -> None:
	""" Delete existing release for a version

	Args:
		owner (str):				GitHub username
		project_name (str):			Name of the GitHub repository
		version (str):				Version of the release to delete
		headers (dict[str, str]):	Headers for GitHub API requests
	"""
	releases_url = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/releases/tags/v{version}"
	release_response = requests.get(releases_url, headers=headers)
	if release_response.status_code == 200:
		release_id = release_response.json()["id"]
		delete_release = requests.delete(
			f"{PROJECT_ENDPOINT}/{owner}/{project_name}/releases/{release_id}",
			headers=headers
		)
		handle_response(delete_release, "Failed to delete existing release")
		stp.info(f"Deleted existing release for v{version}")

def delete_existing_tag(tag_url: str, headers: dict[str, str]) -> None:
	""" Delete existing tag

	Args:
		tag_url (str):				URL of the tag to delete
		headers (dict[str, str]):	Headers for GitHub API requests
	"""
	delete_response = requests.delete(tag_url, headers=headers)
	handle_response(delete_response, "Failed to delete existing tag")
	stp.info(f"Deleted existing tag")

def version_to_int(version: str) -> int:
	""" Version format: major.minor.patch.something_else.... infinitely """
	for letter in "vabr":
		version = version.replace(letter, "")
	version_parts: list[str] = version.split(".")
	total: int = 0
	multiplier: int = 1
	for part in version_parts[::-1]:
		try:
			total += int(part) * multiplier
			multiplier *= 1_000_000	# It means 1 million possible version by dot
		except ValueError:
			pass
	return total

def get_latest_tag(owner: str, project_name: str, version: str, headers: dict[str, str]) -> tuple[str|None, str|None]:
	""" Get latest tag information

	Args:
		owner (str):				GitHub username
		project_name (str):			Name of the GitHub repository
		version (str):				Version to remove from the list of tags
		headers (dict[str, str]):	Headers for GitHub API requests
	Returns:
		str|None: SHA of the latest tag commit, None if no tags exist
		str|None: Version number of the latest tag, None if no tags exist
	"""
	tags_url: str = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/tags"
	response = requests.get(tags_url, headers=headers)
	handle_response(response, "Failed to get tags")
	tags: list[dict] = response.json()
	tags = [tag for tag in tags if tag["name"] != f"v{version}"]
	tags.sort(key=lambda x: version_to_int(x.get("name", "0.0.0")), reverse=True)
	latest_tag_sha: str|None = None if len(tags) == 0 else tags[0]["commit"]["sha"]
	latest_tag_version: str|None = None if len(tags) == 0 else tags[0]["name"].replace("v", "")
	return latest_tag_sha, latest_tag_version

def get_commits_since_tag(owner: str, project_name: str, latest_tag_sha: str|None, headers: dict[str, str]) -> list[dict]:
	""" Get commits since last tag

	Args:
		owner			(str):				GitHub username
		project_name	(str):				Name of the GitHub repository
		latest_tag_sha	(str|None):			SHA of the latest tag commit
		headers			(dict[str, str]):	Headers for GitHub API requests
	Returns:
		list[dict]: List of commits since the last tag
	"""
	commits_url: str = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/commits"
	commits_params: dict[str, str] = {"per_page": "100"}
	
	# If there is a latest tag, use it to get the commits since the tag date
	if latest_tag_sha:

		# Get the date of the latest tag
		tag_commit_url = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/commits/{latest_tag_sha}"
		tag_response = requests.get(tag_commit_url, headers=headers)
		handle_response(tag_response, "Failed to get tag commit")
		tag_date = tag_response.json()["commit"]["committer"]["date"]
		
		# Use the date as the 'since' parameter to get all commits after that date
		commits_params["since"] = tag_date
	
	# Get the commits
	response = requests.get(commits_url, headers=headers, params=commits_params)
	handle_response(response, "Failed to get commits")
	commits: list[dict] = response.json()

	# If there is a latest tag, make sure to commit has the same date as the tag
	if latest_tag_sha:
		commits = [commit for commit in commits if commit["commit"]["committer"]["date"] != tag_date]
	return commits

def generate_changelog(commits: list[dict], owner: str, project_name: str, latest_tag_version: str|None, version: str) -> str:
	""" Generate changelog from commits

	They must follow the conventional commits convention:

		<type>: <description>
	Source:
		https://www.conventionalcommits.org/en/v1.0.0/
	Args:
		commits				(list[dict]):	List of commits to generate changelog from
		owner				(str):			GitHub username
		project_name		(str):			Name of the GitHub repository
		latest_tag_version	(str|None):		Version number of the latest tag
		version				(str):			Current version being released
	Returns:
		str: Generated changelog text
	"""
	commit_groups: dict[str, list[tuple[str, str]]] = {}
	for commit in commits:
		message: str = commit["commit"]["message"].split("\n")[0]
		sha: str = commit["sha"]
		if ":" in message:
			type_, desc = message.split(":", 1)
			type_ = type_.split('(')[0].split('/')[0]
			type_ = "".join(c for c in type_.lower().strip() if c in "abcdefghijklmnopqrstuvwxyz")
			type_ = COMMIT_TYPES.get(type_, type_.title())
			if type_ not in commit_groups:
				commit_groups[type_] = []
			commit_groups[type_].append((desc.strip(), sha))

	changelog = "## Changelog\n\n"
	for type_ in sorted(commit_groups.keys()):
		changelog += f"### {type_}\n"

		# Reverse the list to display the most recent commits in last
		for desc, sha in commit_groups[type_][::-1]:
			changelog += f"- {desc} ([{sha[:7]}](https://github.com/{owner}/{project_name}/commit/{sha}))\n"
		changelog += "\n"
	
	if latest_tag_version:
		changelog += f"**Full Changelog**: https://github.com/{owner}/{project_name}/compare/v{latest_tag_version}...v{version}\n"
	
	return changelog

def create_tag(owner: str, project_name: str, version: str, headers: dict[str, str]) -> None:
	""" Create a new tag

	Args:
		owner (str):				GitHub username
		project_name (str):			Name of the GitHub repository
		version (str):				Version for the new tag
		headers (dict[str, str]):	Headers for GitHub API requests
	"""
	stp.progress(f"Creating tag v{version}")
	create_tag_url = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/git/refs"
	latest_commit_url = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/git/refs/heads/main"
	
	commit_response = requests.get(latest_commit_url, headers=headers)
	if commit_response.status_code != 200:
		raise ValueError(f"Failed to get latest commit: {commit_response.text}")
	
	commit_sha: str = commit_response.json()["object"]["sha"]
	tag_data: dict[str, str] = {
		"ref": f"refs/tags/v{version}",
		"sha": commit_sha
	}
	
	response = requests.post(create_tag_url, headers=headers, json=tag_data)
	handle_response(response, "Failed to create tag")

def create_release(owner: str, project_name: str, version: str, changelog: str, headers: dict[str, str]) -> int:
	""" Create a new release

	Args:
		owner (str):				GitHub username
		project_name (str):			Name of the GitHub repository
		version (str):				Version for the new release
		changelog (str):			Changelog text for the release
		headers (dict[str, str]):	Headers for GitHub API requests
	Returns:
		int: ID of the created release
	"""
	stp.progress(f"Creating release v{version}")
	release_url: str = f"{PROJECT_ENDPOINT}/{owner}/{project_name}/releases"
	release_data: dict[str, str|bool] = {
		"tag_name": f"v{version}",
		"name": f"{project_name} [v{version}]",
		"body": changelog,
		"draft": False,
		"prerelease": False
	}
	
	response = requests.post(release_url, headers=headers, json=release_data)
	handle_response(response, "Failed to create release")
	return response.json()["id"]

def upload_assets(owner: str, project_name: str, release_id: int, build_folder: str, headers: dict[str, str]) -> None:
	""" Upload release assets

	Args:
		owner (str):				GitHub username
		project_name (str):			Name of the GitHub repository
		release_id (int):			ID of the release to upload assets to
		build_folder (str):			Folder containing assets to upload
		headers (dict[str, str]):	Headers for GitHub API requests
	"""
	if not build_folder:
		return
	stp.progress("Uploading assets")
	
	response = requests.get(f"{PROJECT_ENDPOINT}/{owner}/{project_name}/releases/{release_id}", headers=headers)
	handle_response(response, "Failed to get release details")
	upload_url_template: str = response.json()["upload_url"]
	upload_url_base: str = upload_url_template.split("{")[0]
	
	for file in os.listdir(build_folder):
		if file.endswith(".zip"):
			file_path: str = os.path.join(build_folder, file)
			with open(file_path, "rb") as f:
				headers_with_content: dict[str, str] = {
					**headers,
					"Content-Type": "application/zip"
				}
				params: dict[str, str] = {"name": file}
				response = requests.post(
					upload_url_base,
					headers=headers_with_content,
					params=params,
					data=f.read()
				)
				handle_response(response, f"Failed to upload {file}")
				stp.progress(f"Uploaded {file}")

@stp.measure_time(stp.progress, "Uploading to GitHub took")
@stp.handle_error()
def upload_to_github(credentials: dict[str, dict[str, str]], github_config: dict[str, str]) -> str:
	""" Upload the project to GitHub using the credentials and the configuration

	Args:
		credentials (dict[str, dict[str, str]]):	Credentials for the GitHub API
		github_config (dict[str, str]):			Configuration for the GitHub project
	Returns:
		str: Generated changelog text
	"""
	owner, headers = validate_credentials(credentials)
	project_name, version, build_folder = validate_config(github_config)
	
	can_create: bool = handle_existing_tag(owner, project_name, version, headers)
	
	latest_tag_sha, latest_tag_version = get_latest_tag(owner, project_name, version, headers)
	commits = get_commits_since_tag(owner, project_name, latest_tag_sha, headers)
	changelog = generate_changelog(commits, owner, project_name, latest_tag_version, version)
	
	if can_create:
		create_tag(owner, project_name, version, headers)
		release_id = create_release(owner, project_name, version, changelog, headers)
		upload_assets(owner, project_name, release_id, build_folder, headers)	
		stp.info(f"Project {project_name} updated on GitHub!")
	return changelog

