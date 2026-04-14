
# Imports
import re

import pyperclip
import stouputils as stp
from stouputils.typing import JsonDict


# Configuration
def validate_config(pmc_config: dict[str, str]) -> str:
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

	return pmc_config["project_url"]

def convert_markdown_to_bbcode(markdown: str, verbose: bool = True) -> str:
	""" Convert markdown to bbcode for PlanetMinecraft

	Args:
		markdown (str): Markdown text
		verbose (bool): If True, print the conversion comparison

	Returns:
		str: BBcode text

	Examples:
		>>> markdown_text = '''
		... [![Discord](https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord)](https://discord.gg/anxzu6rA9F)
		... ![Discord](https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord)
		... ## Changelog
		...
		... ### Build System
		... - 🚀 Bump version to v1.2.3 ([2111fd2](https://github.com/Stoupy51/LifeSteal/commit/2111fd2f390b80a3aab77a4e7bcbb24b93845e5a))
		...
		...
		...
		... ### Features
		... - ✨ Added new configuration for dropping heart (non pvp) ([cde8749](https://github.com/Stoupy51/LifeSteal/commit/cde8749aa9e447302481f50b9887a0b3a846c7fe))
		...
		... - 🔧 Another feature with multiple newlines before
		...
		... **Full Changelog**: https://github.com/Stoupy51/LifeSteal/compare/v1.2.2...v1.2.3
		... '''
		>>> bbcode = convert_markdown_to_bbcode(markdown_text, verbose=False)
		>>> print(bbcode.strip())
		[url=https://discord.gg/anxzu6rA9F][img]https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord[/img][/url]
		[img]https://img.shields.io/discord/1216400498488377467?label=Discord&logo=discord[/img]
		[h2]Changelog[/h2][h4]Build System[/h4][list]
		[*]🚀 Bump version to v1.2.3 ([url=https://github.com/Stoupy51/LifeSteal/commit/2111fd2f390b80a3aab77a4e7bcbb24b93845e5a]2111fd2[/url])[/*]
		[/list][h4]Features[/h4][list]
		[*]✨ Added new configuration for dropping heart (non pvp) ([url=https://github.com/Stoupy51/LifeSteal/commit/cde8749aa9e447302481f50b9887a0b3a846c7fe]cde8749[/url])[/*]
		[*]🔧 Another feature with multiple newlines before[/*]
		[/list]
		[b]Full Changelog[/b]: [url]https://github.com/Stoupy51/LifeSteal/compare/v1.2.2...v1.2.3[/url]
	"""
	# Make a copy of the original markdown text
	bbcode: str = markdown

	# Step 1: Convert headers (## -> [h2], ### -> [h4])
	bbcode = re.sub(r"^## ([^\n]+)", r"[h2]\1[/h2]", bbcode, flags=re.MULTILINE)
	bbcode = re.sub(r"^### ([^\n]+)", r"[h4]\1[/h4]", bbcode, flags=re.MULTILINE)

	# Step 2: Process lists (group list items by sections)
	list_sections: list[list[str]] = []
	current_list: list[str] = []

	for line in bbcode.split("\n"):
		if line.strip().startswith("- "):
			# Remove the "- " prefix and add to current list
			list_item = line.strip()[2:]
			current_list.append(list_item)
		elif line.strip() == "" and current_list:
			# Empty line within a list, continue (don't break the list)
			continue
		elif current_list:
			# If we have list items and found a non-list, non-empty line,
			# add the current list to our sections and reset
			list_sections.append(current_list)
			current_list = []

	# Add any remaining list items
	if current_list:
		list_sections.append(current_list)

	# Step 3: Convert each list section to BBCode format
	for items in list_sections:
		# Build the markdown pattern with flexible whitespace (including newlines)
		list_md_pattern = "\n+".join([re.escape(f"- {item}") for item in items])
		list_bb = "[list]\n" + "\n".join([f"[*]{item.strip()}[/*]" for item in items]) + "\n[/list]"
		bbcode = re.sub(list_md_pattern, list_bb, bbcode)

	# Step 4: Convert clickable images (must be done before regular links and images)
	# Format: [![alt](img_url)](link_url) -> [url=link_url][img]img_url[/img][/url]
	bbcode = re.sub(r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)", r"[url=\3][img]\2[/img][/url]", bbcode)

	# Step 5: Convert regular images
	# Format: ![alt](img_url) -> [img]img_url[/img]
	bbcode = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r"[img]\2[/img]", bbcode)

	# Step 6: Convert markdown links to BBCode links
	# Format: [text](url) -> [url=url]text[/url]
	bbcode = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[url=\2]\1[/url]", bbcode)

	# Step 7: Convert bold text
	# Format: **text** -> [b]text[/b]
	bbcode = re.sub(r"\*\*([^*]+)\*\*", r"[b]\1[/b]", bbcode)

	# Step 8: Convert plain URLs (not already in BBCode)
	# Look for URLs not already inside [url] or [img] tags
	url_pattern = r"(?<!\[url=|\[url\]|\[img\])(https?://[^\s\]]+)(?!\[/url\]|\[/img\])"
	bbcode = re.sub(url_pattern, r"[url]\1[/url]", bbcode)

	# Step 9: Remove blank lines between sections to create compact format
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

def upload_version(project_url: str, changelog: str) -> None:
	""" Upload new version by opening the project url with the browser

	Args:
		project_url		(str):	Url of the project on PlanetMinecraft to open
		changelog		(str):	Changelog text
	"""
	# Open the project url in the browser
	import subprocess
	subprocess.run(["start", project_url], shell=True)

	# Copy the changelog text to the clipboard
	pyperclip.copy(convert_markdown_to_bbcode(changelog))
	stp.info("Changelog text copied to the clipboard!")


@stp.measure_time(message="Uploading to PlanetMinecraft took")
@stp.handle_error
def upload_to_pmc(pmc_config: JsonDict, changelog: str = "") -> None:
	""" Upload the project to PlanetMinecraft using the configuration

	Disclaimer:
		There is no API for PlanetMinecraft, so everything is done manually.
	Args:
		pmc_config		(dict):		Configuration for the PlanetMinecraft project
		changelog		(str):		Changelog text for the release
	"""
	project_url: str = validate_config(pmc_config)
	upload_version(project_url, changelog)


if __name__ == "__main__":
	import doctest
	doctest.testmod()

