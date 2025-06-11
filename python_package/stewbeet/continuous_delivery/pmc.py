
# Imports
import os
import re

import pyperclip
import stouputils as stp


# Configuration
def validate_config(pmc_config: dict[str, str]) -> tuple[str, str]:
	""" Validate PlanetMinecraft configuration

	Args:
		pmc_config (dict[str, str]): Configuration for the PlanetMinecraft project
	Returns:
		str: Project url on PlanetMinecraft
	"""
	required_keys = ["project_url", "version"]
	error_messages = {
		"project_url": "url of the project on PlanetMinecraft",
		"version": "version of the project",
	}

	for key in required_keys:
		if key not in pmc_config:
			raise ValueError(f"The pmc_config dictionary must contain a '{key}' key, which is the {error_messages[key]}")

	return (
		pmc_config["project_url"],
		pmc_config["version"]
	)

def convert_markdown_to_bbcode(markdown: str, verbose: bool = True) -> str:
	""" Convert markdown to bbcode for PlanetMinecraft

	Args:
		markdown (str): Markdown text
		verbose (bool): If True, print the conversion comparison

	Returns:
		str: BBcode text

	Examples:
		>>> markdown_text = '''
		... ## Changelog
		...
		... ### Build System
		... - 🚀 Bump version to v1.2.3 ([2111fd2](https://github.com/Stoupy51/LifeSteal/commit/2111fd2f390b80a3aab77a4e7bcbb24b93845e5a))
		...
		... ### Features
		... - ✨ Added new configuration for dropping heart (non pvp) ([cde8749](https://github.com/Stoupy51/LifeSteal/commit/cde8749aa9e447302481f50b9887a0b3a846c7fe))
		...
		... **Full Changelog**: https://github.com/Stoupy51/LifeSteal/compare/v1.2.2...v1.2.3
		... '''
		>>> bbcode = convert_markdown_to_bbcode(markdown_text, verbose=True)
		>>> print(bbcode.strip())
		[h2]Changelog[/h2][h4]Build System[/h4][list]
		[*]🚀 Bump version to v1.2.3 ([url=https://github.com/Stoupy51/LifeSteal/commit/2111fd2f390b80a3aab77a4e7bcbb24b93845e5a]2111fd2[/url])[/*]
		[/list][h4]Features[/h4][list]
		[*]✨ Added new configuration for dropping heart (non pvp) ([url=https://github.com/Stoupy51/LifeSteal/commit/cde8749aa9e447302481f50b9887a0b3a846c7fe]cde8749[/url])[/*]
		[/list]
		[b]Full Changelog[/b]: [url]https://github.com/Stoupy51/LifeSteal/compare/v1.2.2...v1.2.3[/url]
	"""
	# Make a copy of the original markdown text
	bbcode: str = markdown

	# Step 1: Convert headers (## -> [h2], ### -> [h4])
	bbcode = re.sub(r"^## ([^\n]+)", r"[h2]\1[/h2]", bbcode, flags=re.MULTILINE)
	bbcode = re.sub(r"^### ([^\n]+)", r"[h4]\1[/h4]", bbcode, flags=re.MULTILINE)

	# Step 2: Process lists (group list items by sections)
	list_sections: list = []
	current_list: list = []

	for line in bbcode.split("\n"):
		if line.strip().startswith("- "):
			# Remove the "- " prefix and add to current list
			list_item = line.strip()[2:]
			current_list.append(list_item)
		elif current_list:
			# If we have list items and found a non-list line,
			# add the current list to our sections and reset
			list_sections.append(current_list)
			current_list = []

	# Add any remaining list items
	if current_list:
		list_sections.append(current_list)

	# Step 3: Convert each list section to BBCode format
	for items in list_sections:
		list_md = "\n".join([f"- {item}" for item in items])
		list_bb = "[list]\n" + "\n".join([f"[*]{item.strip()}[/*]" for item in items]) + "\n[/list]"
		bbcode = bbcode.replace(list_md, list_bb)

	# Step 4: Convert markdown links to BBCode links
	# Format: [text](url) -> [url=url]text[/url]
	bbcode = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[url=\2]\1[/url]", bbcode)

	# Step 5: Convert bold text
	# Format: **text** -> [b]text[/b]
	bbcode = re.sub(r"\*\*([^*]+)\*\*", r"[b]\1[/b]", bbcode)

	# Step 6: Convert plain URLs (not already in BBCode)
	# Look for URLs not already inside [url] tags
	url_pattern = r"(?<!\[url=|\[url\])(https?://[^\s\]]+)(?!\[/url\])"
	bbcode = re.sub(url_pattern, r"[url]\1[/url]", bbcode)

	# Step 7: Remove blank lines between sections to create compact format
	bbcode = re.sub(r"\[/h2]\n+\[h4]", r"[/h2][h4]", bbcode)
	bbcode = re.sub(r"\[/h4]\n+\[list]", r"[/h4][list]", bbcode)
	bbcode = re.sub(r"\[/list]\n+\[h4]", r"[/list][h4]", bbcode)
	bbcode = re.sub(r"\[/list]\n+\[b]", r"[/list]\n[b]", bbcode)

	# Print the conversion comparison if verbose is True
	if verbose:
		print("Original Markdown:")
		print("-" * 40)
		print(markdown)
		print("-" * 40)
		print("\nConverted BBCode:")
		print("-" * 40)
		print(bbcode)
		print("-" * 40)

	return bbcode

def upload_version(project_url: str, version: str, changelog: str) -> None:
	""" Upload new version by opening the project url with the browser

	Args:
		project_url		(str):	Url of the project on PlanetMinecraft to open
		version			(str):	Version number
		changelog		(str):	Changelog text
	"""
	# Open the project url in the browser
	os.system(f"start {project_url}")

	# Copy the changelog text to the clipboard
	pyperclip.copy(convert_markdown_to_bbcode(changelog))
	stp.info("Changelog text copied to the clipboard!")

	# Wait for the user to know if the upload is successful
	stp.progress("Press Enter if you have uploaded the new version")
	input()


@stp.measure_time(stp.progress, "Uploading to PlanetMinecraft took")
@stp.handle_error()
def upload_to_pmc(pmc_config: dict, changelog: str = "") -> None:
	""" Upload the project to PlanetMinecraft using the configuration

	Disclaimer:
		There is no API for PlanetMinecraft, so everything is done manually.
	Args:
		pmc_config		(dict):		Configuration for the PlanetMinecraft project
		changelog		(str):		Changelog text for the release
	"""
	project_url, version = validate_config(pmc_config)
	upload_version(project_url, version, changelog)


if __name__ == "__main__":
	import doctest
	doctest.testmod()

