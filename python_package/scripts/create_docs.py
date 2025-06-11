
# Imports
import sys

import stouputils.applications.automatic_docs as app
from stouputils.io import get_root_path

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
	app.update_documentation(
		root_path=get_root_path(__file__, go_up=2),
		project="StewBeet",
		project_dir="stewbeet",
		author="Stoupy",
		copyright="2025, Stoupy",
		html_logo="https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/templates/extensive/assets/stewbeet_1024x1024.png",
		html_favicon="https://raw.githubusercontent.com/Stoupy51/StewBeet/refs/heads/main/templates/extensive/assets/stewbeet_1024x1024.png",
		github_user="Stoupy51",
		github_repo="stewbeet",
		html_theme="pydata_sphinx_theme",
		version=version,
		skip_undocumented=True,
	)

