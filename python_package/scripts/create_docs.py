
# Imports
import sys
from typing import Any

import stouputils as stp
import stouputils.applications.automatic_docs as app
from stouputils.applications.automatic_docs.sphinx.conf_file import get_sphinx_conf_content

# Constants
STYLE_CONF: str = """
# StewBeet look: the website's fonts and colours, plus a link back to its docs
html_static_path.append("../../python_package/scripts/docs_static")
html_css_files += [
	"https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap",
	"stewbeet.css",
]
html_theme_options["external_links"].insert(0, {
	"url": "https://stewbeet.paralya.fr/docs",
	"name": "Docs",
	"html": "Docs",
})
"""
""" Appended to the generated conf.py, after the stylesheet and theme options it extends. """


# Functions
def get_stewbeet_conf_content(**kwargs: Any) -> str:
	return get_sphinx_conf_content(**kwargs) + STYLE_CONF


# Update documentation
if __name__ == "__main__":

	version: str | None = None
	if len(sys.argv) == 2:
		version = sys.argv[1]
	elif len(sys.argv) == 1:
		pass
	else:
		raise ValueError("Usage: python create_docs.py [version]")

	# Update documentation
	app.sphinx_docs(
		root_path=stp.get_root_path(__file__, go_up=2),
		project="StewBeet",
		project_dir="stewbeet",
		author="Stoupy",
		copyright="2025 - 2026, Stoupy",
		html_logo="https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/stewbeet_1024x1024.png",
		html_favicon="https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/docs/stewbeet_1024x1024.png",
		github_user="Stoupy51",
		github_repo="stewbeet",
		html_theme="breeze",
		version=version,
		skip_undocumented=True,
		external_links=["https://discord.gg/anxzu6rA9F", "https://pypi.org/project/stewbeet/"],
		get_conf_content_function=get_stewbeet_conf_content,
	)

