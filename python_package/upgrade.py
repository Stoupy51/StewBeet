
## Python script that modifies the pyproject.toml to go to the next version
# Imports
import os

# Constants
ROOT: str = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/")
PYPROJECT_PATH = f"{ROOT}/pyproject.toml"
VERSION_KEY = "version = "

def read_file(path: str) -> list[str]:
	"""Read file and return lines"""
	with open(path, "r", encoding="utf-8") as file:
		return file.readlines()

def find_version_line(lines: list[str]) -> int | None:
	"""Find line containing version and return index"""
	for i, line in enumerate(lines):
		if line.startswith(VERSION_KEY):
			return i
	return None

def increment_version(version: str) -> str:
	"""Increment the last number in version string"""
	parts = version.split(".")
	parts[-1] = str(int(parts[-1]) + 1)
	return ".".join(parts)

def extract_version(line: str) -> str:
	"""Extract version number from line"""
	return line.replace(VERSION_KEY, "").strip().replace('"', "")

def write_file(path: str, lines: list[str]) -> None:
	"""Write lines to file"""
	with open(path, "w", encoding="utf-8") as file:
		file.writelines(lines)

# Read the file
lines = read_file(PYPROJECT_PATH)

# Find and update version
version_line = find_version_line(lines)
current_version = None

if version_line is not None:
	# Get and increment version
	current_version = extract_version(lines[version_line])
	new_version = increment_version(current_version)

	# Main
	if __name__ == "__main__":
		
		# Update version line
		lines[version_line] = f'{VERSION_KEY}"{new_version}"\n'
		
		# Write updated file
		write_file(PYPROJECT_PATH, lines)

