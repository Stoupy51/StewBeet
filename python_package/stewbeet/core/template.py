
# Lazy imports (PEP 810), ignored before Python 3.15
from stouputils.lazy import ALWAYS_LAZY

__lazy_modules__ = ALWAYS_LAZY

# Imports
import io
import os
import sys
import zipfile

import requests
import stouputils as stp

# Constants
TEMPLATES_URL: dict[str, dict[str, str]] = {
	"minimal": {
		"url": "https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/tags/__VERSION__/templates/minimal_template.zip",
		"desc": "🔹 A very minimal template using only one `stewbeet` plugin."
	},
	"basic": {
		"url": "https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/tags/__VERSION__/templates/basic_template.zip",
		"desc": "⭐ (Recommended) Complete configuration with all plugins but WITHOUT coded examples."
	},
	"extensive": {
		"url": "https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/tags/__VERSION__/templates/extensive_template.zip",
		"desc": "🌟 Complete template with ALL features and coded examples (ruby ore, tools, etc.)."
	},
}


# Template command for stewbeet
def template_command() -> None:
	""" Handle the 'init/template' command to create a new project from a template.
	If no template name is provided, it asks the user to choose one.

	Ex: `stewbeet init [template_name]`
	"""
	template_name: str | None = sys.argv[2].lower() if len(sys.argv) >= 3 else ""
	if template_name not in TEMPLATES_URL:
		template_name = ask_template_name()
		if template_name is None:
			return

	from importlib.metadata import version
	template_url: str = TEMPLATES_URL[template_name]["url"].replace("__VERSION__", f'v{version("stewbeet")}')
	response: requests.Response = requests.get(template_url)
	if response.status_code != 200:
		stp.error(f"Failed to download the template from '{template_url}'. HTTP status code: {response.status_code}")
		return
	with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
		extract_template(zip_file)
	stp.info("Template initialized successfully!")


def ask_template_name() -> str | None:
	""" Ask which template to use, listing them with their description. None, with an error, for a name not in the list. """
	longest_name_length: int = max(len(name) for name in TEMPLATES_URL)
	string: str = "Available templates:\n" + "".join(
		f"""  - "{name}":{" " * (longest_name_length - len(name))} {data["desc"]}\n""" for name, data in TEMPLATES_URL.items()
	)
	stp.info(string + "\nPlease choose a template from the list above:", end="")
	template_name: str = input().strip().lower()
	if template_name not in TEMPLATES_URL:
		stp.error(f"Template '{template_name}' is not available.")
		return None
	return template_name


def extract_template(zip_file: zipfile.ZipFile) -> None:
	""" Extract the template into the current directory, asking before replacing a file: yes, no, all, or skip all. """
	for member in zip_file.namelist():
		if os.path.exists(member):
			stp.warning(f"File '{member}' already exists. Do you want to replace it? (y/n/all/skip all):", end=" ")
			choice: str = input().strip().lower()
			if choice in ("n", "no"):
				continue
			if choice == "skip all":
				stp.warning("Skipping all existing files.")
				return
			if choice == "all":
				stp.warning("Replacing all existing files.")
				zip_file.extractall(".")
				return
		zip_file.extract(member, ".")

