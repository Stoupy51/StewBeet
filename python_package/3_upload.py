
import os
import sys

LAST_FILES: int = 1
for root, _, files in os.walk("dist"):
	files = sorted(files, key=lambda x: os.path.getmtime(f"dist/{x}"), reverse=True)
	lasts = files[:LAST_FILES * 2] # x2 because we have the .tar.gz and the .whl
	for file in lasts:
		if file.endswith(".tar.gz"):
			os.system(f"{sys.executable} -m twine upload --verbose -r stewbeet dist/{file}")

